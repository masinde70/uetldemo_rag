"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Sidebar, ChatMode } from "@/components/Sidebar";
import { Topbar } from "@/components/Topbar";
import { ChatBubble, Message } from "@/components/chat/ChatBubble";
import { ChatInput } from "@/components/chat/ChatInput";
import { InsightsPanel } from "@/components/InsightsPanel";
import { ScrollArea } from "@/components/ui/scroll-area";
import { motion, AnimatePresence } from "framer-motion";
import { MeshBackground } from "@/components/ui/MeshBackground";
import { useStreamingChat, StreamingMessage } from "@/lib/hooks";

interface ChatResponse {
  answer: string;
  session_id: string;
  sources: string[];
  analytics?: {
    row_count?: number;
    date_range?: { min: string; max: string };
    category_counts?: Record<string, Record<string, number>>;
  };
}

const SESSION_KEY = "sisuiq_session_id";
const MODE_KEY = "sisuiq_mode";
const STREAMING_KEY = "sisuiq_streaming";

export default function Home() {
  const [mode, setMode] = useState<ChatMode>("strategy_qa");
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sources, setSources] = useState<string[]>([]);
  const [analytics, setAnalytics] = useState<ChatResponse["analytics"] | null>(
    null
  );
  const [useStreaming, setUseStreaming] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Streaming chat hook
  const streaming = useStreamingChat({
    mode,
    sessionId,
    onSessionCreated: (id) => setSessionId(id),
    onSourcesReceived: (newSources) => setSources(newSources),
    onAnalyticsReceived: (data) => setAnalytics(data as ChatResponse["analytics"]),
    onError: (error) => console.error("Streaming error:", error),
  });

  // Load persisted state
  useEffect(() => {
    const savedSession = localStorage.getItem(SESSION_KEY);
    const savedMode = localStorage.getItem(MODE_KEY) as ChatMode;
    const savedStreaming = localStorage.getItem(STREAMING_KEY);

    if (savedSession) {
      setSessionId(savedSession);
    }
    if (savedMode) {
      setMode(savedMode);
    }
    if (savedStreaming !== null) {
      setUseStreaming(savedStreaming === "true");
    }
  }, []);

  // Persist streaming preference
  useEffect(() => {
    localStorage.setItem(STREAMING_KEY, String(useStreaming));
  }, [useStreaming]);

  // Persist session ID
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem(SESSION_KEY, sessionId);
    }
  }, [sessionId]);

  // Persist mode
  useEffect(() => {
    localStorage.setItem(MODE_KEY, mode);
  }, [mode]);

  // Scroll to bottom on new messages (both streaming and non-streaming)
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streaming.messages]);

  const handleModeChange = useCallback((newMode: ChatMode) => {
    setMode(newMode);
    // Start a new session when mode changes
    setSessionId(null);
    setMessages([]);
    streaming.clearMessages();
    setSources([]);
    setAnalytics(null);
    localStorage.removeItem(SESSION_KEY);
  }, [streaming]);

  const handleSend = useCallback(
    async (content: string) => {
      // Use streaming mode if enabled
      if (useStreaming) {
        await streaming.sendMessage(content);
        return;
      }

      // Non-streaming mode (original implementation)
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: content,
            mode,
            session_id: sessionId,
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to get response");
        }

        const data: ChatResponse = await response.json();

        // Update session ID
        if (data.session_id && data.session_id !== sessionId) {
          setSessionId(data.session_id);
        }

        // Add assistant message
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: data.answer,
          createdAt: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);

        // Update sources and analytics
        setSources(data.sources || []);
        if (data.analytics) {
          setAnalytics(data.analytics);
        }
      } catch (error) {
        console.error("Chat error:", error);
        // Add error message
        const errorMessage: Message = {
          id: `error-${Date.now()}`,
          role: "assistant",
          content:
            "Sorry, I encountered an error. Please ensure the backend is running and try again.",
          createdAt: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [mode, sessionId, useStreaming, streaming]
  );

  const getPlaceholder = () => {
    switch (mode) {
      case "strategy_qa":
        return "Ask about UETCL's strategic plans and goals...";
      case "actions":
        return "What actions should we take for...";
      case "analytics":
        return "Analyze the outage data and compare to strategy...";
      case "regulatory":
        return "What are ERA's requirements for...";
      default:
        return "Ask a question...";
    }
  };

  return (
    <div className="h-screen flex flex-col bg-bg-primary text-text-primary font-sans relative" data-testid="app-container">
      <MeshBackground />

      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <Topbar />
      </motion.div>

      <div className="flex-1 flex overflow-hidden min-h-0">
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2, ease: "easeOut" }}
          className="flex flex-col flex-shrink-0 min-h-0"
        >
          <Sidebar selectedMode={mode} onModeChange={handleModeChange} />
        </motion.div>

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col bg-transparent relative min-h-0 overflow-hidden" data-testid="chat-area">
          {/* Messages - scrollable container */}
          <div className="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-border-default scrollbar-track-transparent" data-testid="message-list">
            <AnimatePresence initial={false}>
              <div className="max-w-3xl mx-auto pb-4">
                {/* Determine which messages to display based on streaming mode */}
                {(() => {
                  const displayMessages = useStreaming
                    ? streaming.messages.map((m) => ({
                        ...m,
                        content: m.isStreaming ? m.content + "▌" : m.content,
                      }))
                    : messages;
                  const showLoading = useStreaming ? false : isLoading;

                  return (
                    <>
                      {displayMessages.length === 0 ? (
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="h-full flex items-center justify-center py-20"
                        >
                          <div className="text-center max-w-md">
                            <motion.div
                              initial={{ scale: 0.8 }}
                              animate={{ scale: 1 }}
                              transition={{ type: "spring", stiffness: 200, damping: 15 }}
                              className="w-16 h-16 mx-auto mb-4 rounded-full bg-neon-cyan/10 flex items-center justify-center border border-neon-cyan/20"
                            >
                              <span className="text-2xl font-bold text-neon-cyan">S</span>
                            </motion.div>
                            <h2 className="text-xl font-semibold text-text-primary mb-2 font-display">
                              Welcome to SISUiQ
                            </h2>
                            <p className="text-text-secondary text-sm">
                              Your AI copilot for UETCL strategy and ERA regulatory
                              compliance. Select a mode from the sidebar and start asking
                              questions.
                            </p>
                          </div>
                        </motion.div>
                      ) : (
                        <div className="space-y-4">
                          {displayMessages.map((message) => (
                            <ChatBubble key={message.id} message={message} />
                          ))}
                        </div>
                      )}
                      {showLoading && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex gap-3 mb-4"
                        >
                          <div className="w-8 h-8 rounded-full bg-bg-surface-2 flex items-center justify-center flex-shrink-0 border border-border-default">
                            <motion.span
                              animate={{ opacity: [0.4, 1, 0.4] }}
                              transition={{ duration: 1.5, repeat: Infinity }}
                              className="text-neon-cyan text-xs"
                            >
                              ...
                            </motion.span>
                          </div>
                          <div className="bg-bg-surface-2/50 backdrop-blur-sm rounded-lg px-4 py-3 border border-border-default">
                            <div className="flex gap-1">
                              <span className="w-2 h-2 bg-neon-cyan/50 rounded-full animate-bounce" />
                              <span
                                className="w-2 h-2 bg-neon-cyan/50 rounded-full animate-bounce"
                                style={{ animationDelay: "0.1s" }}
                              />
                              <span
                                className="w-2 h-2 bg-neon-cyan/50 rounded-full animate-bounce"
                                style={{ animationDelay: "0.2s" }}
                              />
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </>
                  );
                })()}
                <div ref={messagesEndRef} />
              </div>
            </AnimatePresence>
          </div>

          {/* Input */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <ChatInput
              onSend={handleSend}
              disabled={useStreaming ? streaming.isStreaming : isLoading}
              placeholder={getPlaceholder()}
            />
          </motion.div>
        </main>

        <motion.div
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="flex flex-col min-h-0"
        >
          <InsightsPanel sources={sources} analytics={analytics} mode={mode} />
        </motion.div>
      </div>
    </div>
  );
}
