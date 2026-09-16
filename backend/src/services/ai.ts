import type {
  SignRecognitionService,
  SpeechRecognitionService,
  TextToSpeechService,
  AiRecognitionResult,
  TextToSpeechResult,
} from "../types.js";

export class UnconfiguredSignRecognitionService implements SignRecognitionService {
  async recognizeSign(_input: Uint8Array | string): Promise<AiRecognitionResult> {
    throw new Error("SIGN_AI_NOT_CONFIGURED");
  }
}

export class UnconfiguredSpeechRecognitionService implements SpeechRecognitionService {
  async recognizeSpeech(_input: Uint8Array | string): Promise<AiRecognitionResult> {
    throw new Error("SPEECH_AI_NOT_CONFIGURED");
  }
}

export class UnconfiguredTextToSpeechService implements TextToSpeechService {
  async synthesizeSpeech(_text: string): Promise<TextToSpeechResult> {
    throw new Error("TTS_NOT_CONFIGURED");
  }
}

export interface AiServices {
  signRecognition: SignRecognitionService;
  speechRecognition: SpeechRecognitionService;
  textToSpeech: TextToSpeechService;
}
