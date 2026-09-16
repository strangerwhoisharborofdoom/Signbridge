"""Pydantic schemas for the public SignBridge API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MessageCreate(APIModel):
    sender: Literal["signer", "speaker", "system"]
    input_type: Literal["sign", "speech", "text", "system"]
    text: str = Field(min_length=1, max_length=5000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageResponse(MessageCreate):
    id: UUID
    conversation_id: UUID
    timestamp: datetime


class ConversationResponse(APIModel):
    id: UUID
    status: Literal["active", "ended"]
    created_at: datetime
    updated_at: datetime


class ConversationDetail(APIModel):
    conversation: ConversationResponse
    messages: list[MessageResponse]


class RecognitionResponse(APIModel):
    text: str
    confidence: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SpeechSynthesisResponse(APIModel):
    audio: str
    mime_type: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(APIModel):
    error: str
    message: str
