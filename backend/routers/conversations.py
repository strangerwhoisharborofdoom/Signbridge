"""Conversation and message endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status

from ..database import ConversationStore
from ..models import Conversation, Message
from ..schemas import ConversationDetail, ConversationResponse, MessageCreate, MessageResponse

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


def get_store(request: Request) -> ConversationStore:
    return request.app.state.store


def to_conversation_response(conversation: Conversation) -> ConversationResponse:
    return ConversationResponse.model_validate(conversation, from_attributes=True)


def to_message_response(message: Message) -> MessageResponse:
    return MessageResponse.model_validate(message, from_attributes=True)


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(request: Request) -> ConversationResponse:
    conversation = get_store(request).create_conversation()
    return to_conversation_response(conversation)


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: UUID, request: Request) -> ConversationDetail:
    record = get_store(request).get(conversation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationDetail(
        conversation=to_conversation_response(record.conversation),
        messages=[to_message_response(message) for message in record.messages],
    )


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(conversation_id: UUID, request: Request) -> list[MessageResponse]:
    record = get_store(request).get(conversation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return [to_message_response(message) for message in record.messages]


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    conversation_id: UUID,
    body: MessageCreate,
    request: Request,
) -> MessageResponse:
    store = get_store(request)
    record = store.get(conversation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    message = Message(
        conversation_id=conversation_id,
        sender=body.sender,
        input_type=body.input_type,
        text=body.text.strip(),
        metadata=body.metadata,
    )
    try:
        return to_message_response(store.append_message(conversation_id, message))
    except ValueError as exc:
        if str(exc) == "CONVERSATION_ENDED":
            raise HTTPException(status_code=409, detail="Conversation has ended") from exc
        raise


@router.delete("/{conversation_id}", response_model=ConversationResponse)
async def end_conversation(conversation_id: UUID, request: Request) -> ConversationResponse:
    store = get_store(request)
    if not store.end(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    record = store.get(conversation_id)
    assert record is not None
    return to_conversation_response(record.conversation)
