"""
shared/types/models.py
Shared Pydantic models used across all Lyra Python services.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


# ─────────────────────────────────────────────
# Chat / Message models
# ─────────────────────────────────────────────

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    include_vision_context: Optional[bool] = False


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    tokens_used: Optional[int] = None
    memory_context_used: Optional[bool] = False


# ─────────────────────────────────────────────
# Memory models
# ─────────────────────────────────────────────

class MemoryStoreRequest(BaseModel):
    session_id: str
    role: Literal["user", "assistant"]
    content: str
    tags: Optional[List[str]] = []


class MemoryRecallRequest(BaseModel):
    session_id: str
    query: str
    top_k: Optional[int] = 5


class MemoryRecallResult(BaseModel):
    content: str
    relevance_score: float
    timestamp: Optional[datetime] = None


class MemoryRecallResponse(BaseModel):
    results: List[MemoryRecallResult]
    session_id: str


# ─────────────────────────────────────────────
# Vision context model
# ─────────────────────────────────────────────

class VisionContext(BaseModel):
    description: str
    user_present: bool
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────
# Service health
# ─────────────────────────────────────────────

class HealthResponse(BaseModel):
    service: str
    status: Literal["ok", "error"]
    model: Optional[str] = None
    message: Optional[str] = None
