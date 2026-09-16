export type Sender = "signer" | "speaker" | "system";
export type InputType = "sign" | "speech" | "text" | "system";

export interface Message {
  id: string;
  conversationId: string;
  sender: Sender;
  inputType: InputType;
  text: string;
  timestamp: string;
  metadata: Record<string, unknown>;
}

export interface Conversation {
  id: string;
  status: "active" | "ended";
  createdAt: string;
  updatedAt: string;
}

export interface CreateConversationResult {
  conversation: Conversation;
}

export interface AppendMessageInput {
  sender: Sender;
  inputType: InputType;
  text: string;
  metadata?: Record<string, unknown>;
}

export interface AiRecognitionResult {
  text: string;
  confidence?: number;
  metadata?: Record<string, unknown>;
}

export interface SignRecognitionService {
  recognizeSign(input: Uint8Array | string): Promise<AiRecognitionResult>;
}

export interface SpeechRecognitionService {
  recognizeSpeech(input: Uint8Array | string): Promise<AiRecognitionResult>;
}

export interface TextToSpeechResult {
  audio: Uint8Array | string;
  mimeType: string;
  metadata?: Record<string, unknown>;
}

export interface TextToSpeechService {
  synthesizeSpeech(text: string, options?: { voice?: string; language?: string }): Promise<TextToSpeechResult>;
}
