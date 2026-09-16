import { afterEach, beforeEach, describe, expect, it } from "vitest";
import type { FastifyInstance } from "fastify";
import { buildApp } from "./app.js";

describe("SignBridge conversation API", () => {
  let app: FastifyInstance;

  beforeEach(async () => {
    app = await buildApp({ logger: false, corsOrigin: false });
  });

  afterEach(async () => {
    await app.close();
  });

  it("reports service health", async () => {
    const response = await app.inject({ method: "GET", url: "/api/v1/health" });
    expect(response.statusCode).toBe(200);
    expect(response.json().status).toBe("ok");
  });

  it("creates a conversation and appends a validated message", async () => {
    const create = await app.inject({ method: "POST", url: "/api/v1/conversations" });
    expect(create.statusCode).toBe(200);
    const conversation = create.json().conversation;

    const append = await app.inject({
      method: "POST",
      url: `/api/v1/conversations/${conversation.id}/messages`,
      payload: {
        sender: "speaker",
        inputType: "speech",
        text: "Hello",
      },
    });

    expect(append.statusCode).toBe(201);
    expect(append.json().message).toMatchObject({
      conversationId: conversation.id,
      sender: "speaker",
      inputType: "speech",
      text: "Hello",
    });
  });

  it("rejects an invalid message", async () => {
    const create = await app.inject({ method: "POST", url: "/api/v1/conversations" });
    const id = create.json().conversation.id;

    const response = await app.inject({
      method: "POST",
      url: `/api/v1/conversations/${id}/messages`,
      payload: { sender: "robot", inputType: "speech", text: "" },
    });

    expect(response.statusCode).toBe(400);
  });

  it("returns 404 for an unknown conversation", async () => {
    const id = crypto.randomUUID();
    const response = await app.inject({ method: "GET", url: `/api/v1/conversations/${id}` });
    expect(response.statusCode).toBe(404);
  });

  it("ends a conversation and prevents further messages", async () => {
    const create = await app.inject({ method: "POST", url: "/api/v1/conversations" });
    const id = create.json().conversation.id;

    const clear = await app.inject({ method: "DELETE", url: `/api/v1/conversations/${id}` });
    expect(clear.statusCode).toBe(200);
    expect(clear.json().status).toBe("ended");

    const append = await app.inject({
      method: "POST",
      url: `/api/v1/conversations/${id}/messages`,
      payload: { sender: "speaker", inputType: "speech", text: "Again" },
    });
    expect(append.statusCode).toBe(409);
  });
});
