# SignBridge Backend

Backend/API foundation for SignBridge, a real-time two-way communication application between sign-language users and speech users.

## Member 2 ownership

This backend owns conversation/session APIs, persistence, validation, and provider-neutral AI service contracts. Other team members should integrate through the documented interfaces rather than coupling the frontend directly to providers.

## Proposed API

- `GET /api/v1/health`
- `POST /api/v1/conversations`
- `GET /api/v1/conversations/:conversationId`
- `DELETE /api/v1/conversations/:conversationId`
- `POST /api/v1/conversations/:conversationId/messages`
- `GET /api/v1/conversations/:conversationId/messages`

## Message contract

```json
{
  "sender": "signer | speaker | system",
  "inputType": "sign | speech | text | system",
  "text": "Hello",
  "metadata": {}
}
```

## AI contracts

Provider implementations must satisfy the small interfaces documented in `src/services/ai/interfaces.ts`:

- Sign recognition: input media reference/bytes, output recognized text + confidence + metadata.
- Speech recognition: input audio reference/bytes, output recognized text + confidence + metadata.
- Text-to-speech: input text, output audio reference/data + format metadata.

No provider API keys are stored in source control. Use environment variables.

## Local development

```bash
npm install
cp .env.example .env
npm run dev
```

The default development server uses an in-process store so the API can be demonstrated without a database. The repository is structured so a persistent adapter can replace it without changing the HTTP contract.

## Testing

```bash
npm test
npm run build
```

## Integration notes

Member 1 can call the REST endpoints from the frontend. Member 5 can use the service-layer interfaces or add a real-time transport without changing the conversation data model. Member 3 and Member 4 can implement provider adapters behind the AI contracts.

## Scope / limitations

- This initial backend does not persist raw camera or audio media.
- Authentication is intentionally not mandatory for the MVP; session ownership can be added through middleware later.
- The default store is process-local and should be replaced with a production database adapter before deployment.
