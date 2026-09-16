"""Provider-neutral interfaces for sign, speech and TTS services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RecognitionResult:
    text: str
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SpeechResult:
    audio: bytes
    mime_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


class SignRecognitionService(ABC):
    @abstractmethod
    async def recognize(self, payload: bytes, content_type: str | None = None) -> RecognitionResult:
        raise NotImplementedError


class SpeechRecognitionService(ABC):
    @abstractmethod
    async def recognize(self, payload: bytes, content_type: str | None = None) -> RecognitionResult:
        raise NotImplementedError


class TextToSpeechService(ABC):
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        *,
        voice: str | None = None,
        language: str | None = None,
    ) -> SpeechResult:
        raise NotImplementedError


class UnconfiguredSignRecognitionService(SignRecognitionService):
    async def recognize(self, payload: bytes, content_type: str | None = None) -> RecognitionResult:
        del payload, content_type
        raise RuntimeError("SIGN_AI_NOT_CONFIGURED")


class UnconfiguredSpeechRecognitionService(SpeechRecognitionService):
    async def recognize(self, payload: bytes, content_type: str | None = None) -> RecognitionResult:
        del payload, content_type
        raise RuntimeError("SPEECH_AI_NOT_CONFIGURED")


class UnconfiguredTextToSpeechService(TextToSpeechService):
    async def synthesize(
        self,
        text: str,
        *,
        voice: str | None = None,
        language: str | None = None,
    ) -> SpeechResult:
        del text, voice, language
        raise RuntimeError("TTS_NOT_CONFIGURED")


@dataclass(slots=True)
class AIServiceContainer:
    sign: SignRecognitionService = field(default_factory=UnconfiguredSignRecognitionService)
    speech: SpeechRecognitionService = field(default_factory=UnconfiguredSpeechRecognitionService)
    tts: TextToSpeechService = field(default_factory=UnconfiguredTextToSpeechService)
