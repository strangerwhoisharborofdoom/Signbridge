"""Domain models for SignBridge conversations and messages."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

Sender = Literal["signer", "speaker", "system"]
InputType = Literal["sign", "speech", "text", "system"]
ConversationStatus = Literal["active", "ended"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Message:
    conversation_id: UUID
    sender: Sender
    input_type: InputType
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Conversation:
    id: UUID = field(default_factory=uuid4)
    status: ConversationStatus = "active"
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class ConversationRecord:
    conversation: Conversation
    messages: list[Message] = field(default_factory=list)
