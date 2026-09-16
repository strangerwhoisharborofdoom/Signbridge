"""API tests for SignBridge backend."""

from fastapi.testclient import TestClient

from backend.database import InMemoryConversationStore
from backend.main import create_app
from backend.services.ai import (
    AIServiceContainer,
    RecognitionResult,
    SignRecognitionService,
    SpeechRecognitionService,
    SpeechResult,
    TextToSpeechService,
)


class FakeSign(SignRecognitionService):
    async def recognize(self, payload: bytes, content_type: str | None = None) -> RecognitionResult:
        return RecognitionResult(text="hello", confidence=0.99, metadata={"content_type": content_type})


class FakeSpeech(SpeechRecognitionService):
    async def recognize(self, payload: bytes, content_type: str | None = None) -> RecognitionResult:
        return RecognitionResult(text="How are you?", confidence=0.98)


class FakeTTS(TextToSpeechService):
    async def synthesize(self, text: str, *, voice: str | None = None, language: str | None = None) -> SpeechResult:
        return SpeechResult(audio=b"audio", mime_type="audio/wav", metadata={"text": text})


def test_health() -> None:
    client = TestClient(create_app())
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_conversation_lifecycle() -> None:
    client = TestClient(create_app(store=InMemoryConversationStore()))
    created = client.post("/api/v1/conversations")
    assert created.status_code == 201
    conversation = created.json()
    conversation_id = conversation["id"]

    created_message = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"sender": "speaker", "input_type": "speech", "text": "Hello"},
    )
    assert created_message.status_code == 201
    assert created_message.json()["text"] == "Hello"

    detail = client.get(f"/api/v1/conversations/{conversation_id}")
    assert detail.status_code == 200
    assert len(detail.json()["messages"]) == 1

    ended = client.delete(f"/api/v1/conversations/{conversation_id}")
    assert ended.status_code == 200
    assert ended.json()["status"] == "ended"

    rejected = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"sender": "speaker", "input_type": "speech", "text": "Again"},
    )
    assert rejected.status_code == 409


def test_validation() -> None:
    client = TestClient(create_app())
    created = client.post("/api/v1/conversations")
    conversation_id = created.json()["id"]

    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"sender": "robot", "input_type": "speech", "text": ""},
    )
    assert response.status_code == 422


def test_missing_conversation() -> None:
    client = TestClient(create_app())
    response = client.get("/api/v1/conversations/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_ai_adapters() -> None:
    ai = AIServiceContainer(sign=FakeSign(), speech=FakeSpeech(), tts=FakeTTS())
    client = TestClient(create_app(ai=ai))

    sign = client.post(
        "/api/v1/ai/sign/recognize",
        files={"file": ("frame.jpg", b"frame", "image/jpeg")},
    )
    assert sign.status_code == 200
    assert sign.json()["text"] == "hello"

    speech = client.post(
        "/api/v1/ai/speech/recognize",
        files={"file": ("voice.webm", b"audio", "audio/webm")},
    )
    assert speech.status_code == 200
    assert speech.json()["text"] == "How are you?"

    tts = client.post("/api/v1/ai/tts", json={"text": "Hello", "language": "en-IN"})
    assert tts.status_code == 200
    assert tts.json()["mime_type"] == "audio/wav"


def test_unconfigured_ai_returns_503() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/ai/speech/recognize",
        files={"file": ("voice.webm", b"audio", "audio/webm")},
    )
    assert response.status_code == 503
