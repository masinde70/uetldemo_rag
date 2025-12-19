# Streaming Responses

SISUiQ supports real-time token-by-token streaming for chat responses, providing a ChatGPT-like experience where users see the AI's response as it's being generated.

## Architecture Overview

```
┌─────────────┐     SSE      ┌─────────────┐    SSE     ┌─────────────┐
│   Browser   │ ──────────▶  │  Next.js    │ ────────▶  │   FastAPI   │
│  (React)    │ ◀──────────  │  API Route  │ ◀────────  │   Backend   │
└─────────────┘   tokens     └─────────────┘  tokens    └─────────────┘
                                                              │
                                                              ▼
                                                        ┌─────────────┐
                                                        │   OpenAI    │
                                                        │   Stream    │
                                                        └─────────────┘
```

## Backend Implementation

### Streaming Endpoint

**POST /api/chat/stream**

Returns Server-Sent Events (SSE) with the following event types:

| Event | Data | Description |
|-------|------|-------------|
| `start` | `{session_id, sources}` | Initial metadata |
| `token` | `{content}` | Individual token |
| `done` | `{content, sources, analytics}` | Complete response |
| `error` | `{message}` | Error occurred |

### Example SSE Stream

```
event: start
data: {"session_id": "uuid", "sources": ["doc1.pdf", "doc2.pdf"]}

event: token
data: {"content": "The"}

event: token
data: {"content": " strategic"}

event: token
data: {"content": " plan"}

...

event: done
data: {"content": "The strategic plan...", "sources": [...], "analytics": null}
```

### Backend Files

- `backend/routers/chat_stream.py` - SSE endpoint handler
- `backend/services/llm_stream.py` - OpenAI streaming wrapper

### Configuration

The streaming endpoint uses the same environment variables as the regular chat:

```env
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4o  # or gpt-4-turbo, gpt-3.5-turbo
```

## Frontend Implementation

### useStreamingChat Hook

The `useStreamingChat` hook provides a complete solution for streaming chat:

```typescript
import { useStreamingChat } from "@/lib/hooks";

function ChatComponent() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sources, setSources] = useState<string[]>([]);

  const { messages, isStreaming, sendMessage, clearMessages, abortStream } =
    useStreamingChat({
      mode: "strategy_qa",
      sessionId,
      onSessionCreated: setSessionId,
      onSourcesReceived: setSources,
      onError: (error) => console.error(error),
    });

  return (
    <div>
      {messages.map((msg) => (
        <div key={msg.id}>
          <strong>{msg.role}:</strong> {msg.content}
          {msg.isStreaming && <span className="cursor">▌</span>}
        </div>
      ))}

      <button onClick={() => sendMessage("Hello!")}>Send</button>
      {isStreaming && <button onClick={abortStream}>Cancel</button>}
    </div>
  );
}
```

### Hook Options

| Option | Type | Description |
|--------|------|-------------|
| `mode` | `string` | Chat mode (strategy_qa, actions, analytics, regulatory) |
| `sessionId` | `string \| null` | Current session ID |
| `onSessionCreated` | `(id: string) => void` | Called when new session is created |
| `onSourcesReceived` | `(sources: string[]) => void` | Called with source citations |
| `onAnalyticsReceived` | `(data: object) => void` | Called with analytics data |
| `onError` | `(error: Error) => void` | Error handler |

### Hook Return Values

| Value | Type | Description |
|-------|------|-------------|
| `messages` | `StreamingMessage[]` | All messages in conversation |
| `isStreaming` | `boolean` | Whether currently streaming |
| `sendMessage` | `(content: string) => Promise<void>` | Send a new message |
| `clearMessages` | `() => void` | Clear all messages |
| `abortStream` | `() => void` | Cancel current stream |

### Message Type

```typescript
interface StreamingMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
  isStreaming?: boolean;
}
```

## Switching Between Streaming and Non-Streaming

The application supports both streaming and non-streaming modes. To switch:

### Using Streaming (Default for Better UX)

```typescript
import { useStreamingChat } from "@/lib/hooks";

const { messages, sendMessage, isStreaming } = useStreamingChat({
  mode,
  sessionId,
  onSessionCreated: setSessionId,
});
```

### Using Non-Streaming (Original)

```typescript
const response = await fetch("/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message, mode, session_id: sessionId }),
});
const data = await response.json();
```

## Performance Considerations

### Backend

- Tokens are yielded immediately as received from OpenAI
- Database writes happen after streaming completes
- Connection timeout: 5 minutes default

### Frontend

- Uses native `ReadableStream` API for efficient memory usage
- Supports `AbortController` for cancellation
- Debounces re-renders during rapid token arrival

## Error Handling

### Network Errors

The hook automatically handles network errors and displays an error message:

```typescript
onError: (error) => {
  toast.error(`Chat error: ${error.message}`);
}
```

### Stream Cancellation

Users can cancel an in-progress stream:

```typescript
const { abortStream, isStreaming } = useStreamingChat(options);

// In your UI
{isStreaming && (
  <button onClick={abortStream}>Stop generating</button>
)}
```

## Testing

### Manual Testing

1. Start the backend: `cd backend && uvicorn backend.main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Open the chat interface and send a message
4. Observe tokens appearing in real-time

### Curl Testing

```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "What is UETCL?", "mode": "strategy_qa"}'
```

## Dependencies

### Backend
- `sse-starlette==1.8.2` - SSE support for FastAPI

### Frontend
- Native browser APIs (no additional dependencies)
- Uses React hooks for state management
