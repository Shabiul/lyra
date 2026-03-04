"""
services/llm-core/main.py
FastAPI app — exposes Lyra's chat endpoints.
Run with: uvicorn main:app --host 0.0.0.0 --port 8001 --reload
"""

import sys
import os
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from shared.types.models import ChatRequest, ChatResponse, HealthResponse
from shared.utils.config_loader import CONFIG
from chat import chat, chat_stream, reset_session


app = FastAPI(
    title="Lyra — LLM Core",
    description="Lyra's brain: personality, chat, and Ollama integration.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────

@app.get("/status", response_model=HealthResponse)
async def status():
    import httpx
    ollama_host = CONFIG["ollama"]["host"]
    model = CONFIG["ollama"]["model"]
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{ollama_host}/api/tags")
            r.raise_for_status()
        return HealthResponse(service="llm-core", status="ok", model=model)
    except Exception as e:
        return HealthResponse(
            service="llm-core",
            status="error",
            model=model,
            message=f"Ollama unreachable: {str(e)}"
        )


# ─────────────────────────────────────────────
# Standard chat (REST)
# ─────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        reply = await chat(
            session_id=req.session_id,
            user_message=req.message,
        )
        return ChatResponse(
            reply=reply,
            session_id=req.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# Chat with full context (vision + memory)
# ─────────────────────────────────────────────

@app.post("/chat/contextual", response_model=ChatResponse)
async def chat_contextual(
    req: ChatRequest,
    vision_context: str = None,
    memory_context: str = None,
):
    try:
        reply = await chat(
            session_id=req.session_id,
            user_message=req.message,
            vision_context=vision_context,
            memory_context=memory_context,
        )
        return ChatResponse(
            reply=reply,
            session_id=req.session_id,
            memory_context_used=memory_context is not None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# Reset session
# ─────────────────────────────────────────────

@app.post("/reset")
async def reset(session_id: str = "default"):
    reset_session(session_id)
    return {"status": "ok", "session_id": session_id, "message": "Session cleared."}


# ─────────────────────────────────────────────
# Streaming chat via WebSocket
# ─────────────────────────────────────────────

@app.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    """
    WebSocket streaming chat.
    Client sends: { "message": "...", "session_id": "..." }
    Server streams back tokens as plain text, ends with [END]
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            session_id = data.get("session_id", "default")
            vision_context = data.get("vision_context", None)
            memory_context = data.get("memory_context", None)

            async for token in chat_stream(
                session_id=session_id,
                user_message=message,
                vision_context=vision_context,
                memory_context=memory_context,
            ):
                await websocket.send_text(token)

            await websocket.send_text("[END]")

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(f"[ERROR] {str(e)}")
        await websocket.close()
