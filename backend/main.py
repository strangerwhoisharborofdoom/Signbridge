"""SignBridge FastAPI application entrypoint."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import ConversationStore, InMemoryConversationStore
from .routers.ai import router as ai_router
from .routers.conversations import router as conversations_router
from .services.ai import AIServiceContainer


def create_app(
    *,
    store: ConversationStore | None = None,
    ai: AIServiceContainer | None = None,
) -> FastAPI:
    app = FastAPI(
        title="SignBridge Backend",
        version="0.1.0",
        description="Backend API for real-time two-way sign/speech communication.",
    )

    origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.store = store or InMemoryConversationStore()
    app.state.ai = ai or AIServiceContainer()

    @app.get("/api/v1/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "signbridge-backend"}

    app.include_router(conversations_router)
    app.include_router(ai_router)
    return app


app = create_app()
