"""AI adapter endpoints used by the sign, speech and integration agents."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from ..services.ai import AIServiceContainer
from ..schemas import RecognitionResponse, SpeechSynthesisResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


class TextToSpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    voice: str | None = Field(default=None, max_length=100)
    language: str | None = Field(default=None, max_length=35)


def get_ai(request: Request) -> AIServiceContainer:
    return request.app.state.ai


@router.post("/sign/recognize", response_model=RecognitionResponse)
async def recognize_sign(request: Request, file: Annotated[UploadFile, File(...)]) -> RecognitionResponse:
    payload = await file.read()
    try:
        result = await get_ai(request).sign.recognize(payload, file.content_type)
    except RuntimeError as exc:
        if str(exc) == "SIGN_AI_NOT_CONFIGURED":
            raise HTTPException(status_code=503, detail="Sign recognition service is not configured") from exc
        raise
    return RecognitionResponse(text=result.text, confidence=result.confidence, metadata=result.metadata)


@router.post("/speech/recognize", response_model=RecognitionResponse)
async def recognize_speech(request: Request, file: Annotated[UploadFile, File(...)]) -> RecognitionResponse:
    payload = await file.read()
    try:
        result = await get_ai(request).speech.recognize(payload, file.content_type)
    except RuntimeError as exc:
        if str(exc) == "SPEECH_AI_NOT_CONFIGURED":
            raise HTTPException(status_code=503, detail="Speech recognition service is not configured") from exc
        raise
    return RecognitionResponse(text=result.text, confidence=result.confidence, metadata=result.metadata)


@router.post("/tts", response_model=SpeechSynthesisResponse)
async def synthesize(request: Request, body: TextToSpeechRequest) -> SpeechSynthesisResponse:
    try:
        result = await get_ai(request).tts.synthesize(body.text, voice=body.voice, language=body.language)
    except RuntimeError as exc:
        if str(exc) == "TTS_NOT_CONFIGURED":
            raise HTTPException(status_code=503, detail="Text-to-speech service is not configured") from exc
        raise
    import base64

    return SpeechSynthesisResponse(
        audio=base64.b64encode(result.audio).decode("ascii"),
        mime_type=result.mime_type,
        metadata=result.metadata,
    )
