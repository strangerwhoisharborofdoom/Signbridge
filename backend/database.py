"""Persistence abstraction and a safe in-memory MVP implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from threading import RLock
from uuid import UUID

from .models import Conversation, ConversationRecord, Message


class ConversationStore(ABC):
    """Persistence contract used by routers/services."""

    @abstractmethod
    def create_conversation(self) -> Conversation:
        raise NotImplementedError

    @abstractmethod
    def get(self, conversation_id: UUID) -> ConversationRecord | None:
        raise NotImplementedError

    @abstractmethod
    def append_message(self, conversation_id: UUID, message: Message) -> Message:
        raise NotImplementedError

    @abstractmethod
    def end(self, conversation_id: UUID) -> bool:
        raise NotImplementedError


class InMemoryConversationStore(ConversationStore):
    """Development/MVP store. Replace with SQL-backed implementation later."""

    def __init__(self) -> None:
        self._records: dict[UUID, ConversationRecord] = {}
        self._lock = RLock()

    def create_conversation(self) -> Conversation:
        conversation = Conversation()
        with self._lock:
            self._records[conversation.id] = ConversationRecord(conversation=conversation)
        return conversation

    def get(self, conversation_id: UUID) -> ConversationRecord | None:
        with self._lock:
            return self._records.get(conversation_id)

    def append_message(self, conversation_id: UUID, message: Message) -> Message:
        with self._lock:
            record = self._records.get(conversation_id)
            if record is None:
                raise KeyError("CONVERSATION_NOT_FOUND")
            if record.conversation.status == "ended":
                raise ValueError("CONVERSATION_ENDED")
            message.conversation_id = conversation_id
            record.messages.append(message)
            record.conversation.updated_at = message.timestamp
            return message

    def end(self, conversation_id: UUID) -> bool:
        with self._lock:
            record = self._records.get(conversation_id)
            if record is None:
                return False
            record.conversation.status = "ended"
            record.conversation.updated_at = record.conversation.updated_at
            return True
