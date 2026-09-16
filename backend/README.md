# SignBridge Backend

Member 2 owns the backend/API/database layer.

## Stack

- Node.js
- TypeScript
- Fastify
- Zod
- Vitest

The MVP currently uses an in-memory persistence adapter. This intentionally keeps the API contract stable while allowing a future PostgreSQL/SQLite adapter without changing frontend integration.

## Run

```bash
npm install
npm run dev
```

The default port is `4000`.

## Production build

```bash
npm run build
npm start
```

## Test

```bash
npm test
```

## API

### GET `/api/v1/health`

Returns backend health and timestamp.

### POST `/api/v1/conversations`

Create a conversation.

Request:

```json
{
  "language": "en"
}
```

`language` is optional and defaults to `en`.

### GET `/api/v1/conversations/:conversationId`

Return one conversation including its messages.

### POST `/api/v1/conversations/:conversationId/messages`

Append a message.

Request:

```json
{
  "sender": "signer",
  "inputType": "sign",
  "text": "hello",
  "metadata": {
    "confidence": 0.94
  }
}
```

Allowed `sender`: `signer`, `speaker`, `system`.

Allowed `inputType`: `sign`, `speech`, `text`.

`text` must contain 1-5000 characters. `metadata` is optional JSON data.

### DELETE `/api/v1/conversations/:conversationId/messages`

Clear messages while keeping the conversation session.

### POST `/api/v1/conversations/:conversationId/end`

Mark the conversation as ended.

Ended conversations reject new messages with HTTP 409.

## Error shape

Errors use a predictable response:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": []
  }
}
```

Common codes are `VALIDATION_ERROR`, `NOT_FOUND`, `CONVERSATION_ENDED`, and `INTERNAL_ERROR`.

## AI contracts

The backend exposes provider-neutral service contracts for:

- `SignRecognitionService`
- `SpeechRecognitionService`
- `TextToSpeechService`

Members 3 and 4 should implement adapters against these interfaces rather than coupling routes to a specific provider.

## Integration notes

The frontend can use REST under `/api/v1`. Member 5 can add WebSocket/SSE on top of the same conversation/message model without storing raw camera or microphone payloads.

The in-memory adapter is process-local and is not suitable for multi-instance production deployment. Replace it with a persistent adapter before production scaling.
