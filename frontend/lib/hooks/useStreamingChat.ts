/**
 * React hook for streaming chat responses using Server-Sent Events (SSE).
 *
 * Provides real-time token-by-token streaming from the backend,
 * enabling a ChatGPT-like typing experience.
 */

import { useState, useCallback, useRef } from "react";

export interface StreamingMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
  isStreaming?: boolean;
}

export interface StreamingChatOptions {
  mode: string;
  sessionId: string | null;
  onSessionCreated?: (sessionId: string) => void;
  onSourcesReceived?: (sources: string[]) => void;
  onAnalyticsReceived?: (analytics: Record<string, unknown>) => void;
  onError?: (error: Error) => void;
}

export interface StreamingChatResult {
  messages: StreamingMessage[];
  isStreaming: boolean;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  abortStream: () => void;
}

/**
 * Hook for managing streaming chat interactions.
 *
 * @example
 * ```tsx
 * const { messages, isStreaming, sendMessage } = useStreamingChat({
 *   mode: "strategy_qa",
 *   sessionId: null,
 *   onSessionCreated: (id) => setSessionId(id),
 *   onSourcesReceived: (sources) => setSources(sources),
 * });
 *
 * // Send a message
 * await sendMessage("What is UETCL's strategic vision?");
 * ```
 */
export function useStreamingChat(
  options: StreamingChatOptions
): StreamingChatResult {
  const { mode, sessionId, onSessionCreated, onSourcesReceived, onAnalyticsReceived, onError } =
    options;

  const [messages, setMessages] = useState<StreamingMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const abortStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsStreaming(false);
    }
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      // Add user message immediately
      const userMessage: StreamingMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Create placeholder for assistant response
      const assistantId = `assistant-${Date.now()}`;
      const assistantMessage: StreamingMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        createdAt: new Date().toISOString(),
        isStreaming: true,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      setIsStreaming(true);

      // Create abort controller for this request
      abortControllerRef.current = new AbortController();

      try {
        const response = await fetch("/api/chat/stream", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: content,
            mode,
            session_id: sessionId,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error("No response body");
        }

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Process complete SSE events
          const lines = buffer.split("\n");
          buffer = lines.pop() || ""; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith("event:")) {
              // Store event type for next data line
              continue;
            }

            if (line.startsWith("data:")) {
              const data = line.slice(5).trim();
              if (!data) continue;

              try {
                const parsed = JSON.parse(data);

                // Handle different event types based on data content
                if ("session_id" in parsed && "sources" in parsed) {
                  // Start event
                  if (parsed.session_id && onSessionCreated) {
                    onSessionCreated(parsed.session_id);
                  }
                  if (parsed.sources && onSourcesReceived) {
                    onSourcesReceived(parsed.sources);
                  }
                } else if ("content" in parsed && !("sources" in parsed)) {
                  // Token event - append content
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantId
                        ? { ...msg, content: msg.content + parsed.content }
                        : msg
                    )
                  );
                } else if ("content" in parsed && "sources" in parsed) {
                  // Done event
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantId
                        ? { ...msg, isStreaming: false }
                        : msg
                    )
                  );
                  if (parsed.analytics && onAnalyticsReceived) {
                    onAnalyticsReceived(parsed.analytics);
                  }
                } else if ("message" in parsed) {
                  // Error event
                  throw new Error(parsed.message);
                }
              } catch (parseError) {
                // Ignore JSON parse errors for incomplete data
                if (parseError instanceof SyntaxError) {
                  continue;
                }
                throw parseError;
              }
            }
          }
        }
      } catch (error) {
        if (error instanceof Error && error.name === "AbortError") {
          // Stream was aborted, update message state
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId
                ? { ...msg, isStreaming: false, content: msg.content || "(Cancelled)" }
                : msg
            )
          );
        } else {
          // Handle other errors
          const errorMessage =
            error instanceof Error ? error.message : "Unknown error occurred";

          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId
                ? {
                    ...msg,
                    isStreaming: false,
                    content: `Sorry, an error occurred: ${errorMessage}`,
                  }
                : msg
            )
          );

          if (onError && error instanceof Error) {
            onError(error);
          }
        }
      } finally {
        setIsStreaming(false);
        abortControllerRef.current = null;
      }
    },
    [mode, sessionId, onSessionCreated, onSourcesReceived, onAnalyticsReceived, onError]
  );

  return {
    messages,
    isStreaming,
    sendMessage,
    clearMessages,
    abortStream,
  };
}

export default useStreamingChat;
