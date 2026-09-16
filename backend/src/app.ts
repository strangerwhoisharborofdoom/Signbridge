import Fastify, { type FastifyInstance } from "fastify";
import cors from "@fastify/cors";
import sensible from "@fastify/sensible";
import { z } from "zod";
import { InMemoryConversationStore, type ConversationStore } from "./store.js";
import {
  UnconfiguredSignRecognitionService,
  UnconfiguredSpeechRecognitionService,
  UnconfiguredTextToSpeechService,
  type AiServices,
} from "./services/ai.js";

const messageSchema = z.object({
  sender: z.enum(["signer", "speaker", "system"]),
  inputType: z.enum(["sign", "speech", "text", "system"]),
  text: z.string().trim().min(1).max(5000),
  metadata: z.record(z.string(), z.unknown()).optional(),
});

const idParamsSchema = z.object({
  conversationId: z.string().uuid(),
});

export interface AppOptions {
  store?: ConversationStore;
  ai?: AiServices;
  corsOrigin?: string;
  logger?: boolean;
}

function getErrorCode(error: unknown): string | undefined {
  return error instanceof Error ? error.message : undefined;
}

export async function buildApp(options: AppOptions = {}): Promise<FastifyInstance> {
  const app = Fastify({ logger: options.logger ?? true });
  const store = options.store ?? new InMemoryConversationStore();
  const ai: AiServices = options.ai ?? {
    signRecognition: new UnconfiguredSignRecognitionService(),
    speechRecognition: new UnconfiguredSpeechRecognitionService(),
    textToSpeech: new UnconfiguredTextToSpeechService(),
  };

  await app.register(sensible);
  await app.register(cors, {
    origin: options.corsOrigin ?? process.env.CORS_ORIGIN ?? true,
  });

  app.get("/api/v1/health", async () => ({
    status: "ok",
    service: "signbridge-backend",
    timestamp: new Date().toISOString(),
  }));

  app.post("/api/v1/conversations", async () => ({
    conversation: store.createConversation(),
  }));

  app.get("/api/v1/conversations/:conversationId", async (request, reply) => {
    const parsed = idParamsSchema.safeParse(request.params);
    if (!parsed.success) return reply.badRequest("Invalid conversationId");

    const conversation = store.getConversation(parsed.data.conversationId);
    if (!conversation) return reply.notFound("Conversation not found");

    return {
      conversation,
      messages: store.listMessages(conversation.id),
    };
  });

  app.get("/api/v1/conversations/:conversationId/messages", async (request, reply) => {
    const parsed = idParamsSchema.safeParse(request.params);
    if (!parsed.success) return reply.badRequest("Invalid conversationId");

    if (!store.getConversation(parsed.data.conversationId)) {
      return reply.notFound("Conversation not found");
    }

    return { messages: store.listMessages(parsed.data.conversationId) };
  });

  app.post("/api/v1/conversations/:conversationId/messages", async (request, reply) => {
    const params = idParamsSchema.safeParse(request.params);
    if (!params.success) return reply.badRequest("Invalid conversationId");

    const body = messageSchema.safeParse(request.body);
    if (!body.success) {
      return reply.badRequest({
        message: "Invalid message payload",
        issues: body.error.issues,
      });
    }

    if (!store.getConversation(params.data.conversationId)) {
      return reply.notFound("Conversation not found");
    }

    try {
      const message = store.appendMessage(params.data.conversationId, body.data);
      return reply.code(201).send({ message });
    } catch (error) {
      const code = getErrorCode(error);
      if (code === "CONVERSATION_ENDED") return reply.conflict("Conversation has ended");
      throw error;
    }
  });

  app.delete("/api/v1/conversations/:conversationId", async (request, reply) => {
    const parsed = idParamsSchema.safeParse(request.params);
    if (!parsed.success) return reply.badRequest("Invalid conversationId");

    const cleared = store.clearConversation(parsed.data.conversationId);
    if (!cleared) return reply.notFound("Conversation not found");

    return { conversationId: parsed.data.conversationId, status: "ended" };
  });

  // AI service handles are intentionally exposed only inside the app context for
  // integration code. HTTP provider credentials remain outside the route layer.
  app.decorate("aiServices", ai);

  app.setErrorHandler((error, _request, reply) => {
    requestLogError(error);
    if (reply.sent) return;
    return reply.code(error.statusCode && error.statusCode >= 400 ? error.statusCode : 500).send({
      error: {
        code: error.code ?? "INTERNAL_ERROR",
        message: error.statusCode && error.statusCode < 500 ? error.message : "Internal server error",
      },
    });
  });

  return app;
}

function requestLogError(error: unknown): void {
  // Avoid leaking provider credentials or arbitrary object values into HTTP errors.
  if (process.env.NODE_ENV !== "test") console.error(error instanceof Error ? error.message : "Unknown error");
}
