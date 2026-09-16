import type { AppendMessageInput, Conversation, Message } from "./types.js";

export interface ConversationStore {
  createConversation(): Conversation;
  getConversation(id: string): Conversation | undefined;
  listMessages(conversationId: string): Message[];
  appendMessage(conversationId: string, input: AppendMessageInput): Message;
  clearConversation(id: string): boolean;
}

/**
 * MVP store. The public store interface is intentionally persistence-agnostic,
 * so PostgreSQL/SQLite can be introduced later without changing route contracts.
 */
export class InMemoryConversationStore implements ConversationStore {
  private readonly conversations = new Map<string, Conversation>();
  private readonly messages = new Map<string, Message[]>();

  createConversation(): Conversation {
    const now = new Date().toISOString();
    const conversation: Conversation = {
      id: crypto.randomUUID(),
      status: "active",
      createdAt: now,
      updatedAt: now,
    };
    this.conversations.set(conversation.id, conversation);
    this.messages.set(conversation.id, []);
    return conversation;
  }

  getConversation(id: string): Conversation | undefined {
    return this.conversations.get(id);
  }

  listMessages(conversationId: string): Message[] {
    return [...(this.messages.get(conversationId) ?? [])];
  }

  appendMessage(conversationId: string, input: AppendMessageInput): Message {
    const conversation = this.conversations.get(conversationId);
    if (!conversation) {
      throw new Error("CONVERSATION_NOT_FOUND");
    }
    if (conversation.status !== "active") {
      throw new Error("CONVERSATION_ENDED");
    }

    const message: Message = {
      id: crypto.randomUUID(),
      conversationId,
      sender: input.sender,
      inputType: input.inputType,
      text: input.text,
      timestamp: new Date().toISOString(),
      metadata: input.metadata ?? {},
    };

    const messages = this.messages.get(conversationId) ?? [];
    messages.push(message);
    this.messages.set(conversationId, messages);
    conversation.updatedAt = message.timestamp;
    return message;
  }

  clearConversation(id: string): boolean {
    const conversation = this.conversations.get(id);
    if (!conversation) return false;

    conversation.status = "ended";
    conversation.updatedAt = new Date().toISOString();
    this.messages.set(id, []);
    return true;
  }
}
