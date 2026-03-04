"""
services/llm-core/chat.py
Core chat engine — manages conversation sessions and talks to Ollama.
"""

import httpx
import json
import sys
import os
from typing import AsyncGenerator

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from shared.utils.config_loader import CONFIG
from personality import build_system_prompt


OLLAMA_HOST = CONFIG["ollama"]["host"]
OLLAMA_MODEL = CONFIG["ollama"]["model"]
OLLAMA_OPTIONS = CONFIG["ollama"]["options"]
OLLAMA_TIMEOUT = CONFIG["ollama"]["timeout"]

# In-memory session store: session_id → list of messages
# (short-term context window, complements long-term memory service)
_sessions: dict[str, list[dict]] = {}


def get_session(session_id: str) -> list[dict]:
    if session_id not in _sessions:
        _sessions[session_id] = []
    return _sessions[session_id]


def reset_session(session_id: str):
    _sessions[session_id] = []


def trim_session(session_id: str, max_turns: int = None):
    """Keep only the last N turns to avoid context overflow."""
    max_turns = max_turns or CONFIG["memory"]["short_term_turns"]
    history = _sessions.get(session_id, [])
    if len(history) > max_turns * 2:
        _sessions[session_id] = history[-(max_turns * 2):]


async def chat(
    session_id: str,
    user_message: str,
    vision_context: str = None,
    memory_context: str = None,
) -> str:
    """
    Send a message to Ollama and return Lyra's reply.
    Maintains per-session conversation history.
    """
    history = get_session(session_id)

    # Build messages payload
    system_prompt = build_system_prompt(
        vision_context=vision_context,
        memory_context=memory_context
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": OLLAMA_OPTIONS,
    }

    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload
        )
        response.raise_for_status()
        data = response.json()

    reply = data["message"]["content"].strip()

    # Update session history
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    trim_session(session_id)

    return reply


async def chat_stream(
    session_id: str,
    user_message: str,
    vision_context: str = None,
    memory_context: str = None,
) -> AsyncGenerator[str, None]:
    """
    Streaming version — yields text chunks as Ollama generates them.
    Used by the WebSocket endpoint in main.py.
    """
    history = get_session(session_id)

    system_prompt = build_system_prompt(
        vision_context=vision_context,
        memory_context=memory_context
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": True,
        "options": OLLAMA_OPTIONS,
    }

    full_reply = ""

    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        async with client.stream("POST", f"{OLLAMA_HOST}/api/chat", json=payload) as response:
            async for line in response.aiter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                token = chunk.get("message", {}).get("content", "")
                if token:
                    full_reply += token
                    yield token
                if chunk.get("done"):
                    break

    # Save to history after stream completes
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": full_reply})
    trim_session(session_id)
