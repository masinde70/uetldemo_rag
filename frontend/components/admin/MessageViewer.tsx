"use client";

import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/api";
import { ScrollArea } from "@/components/ui/scroll-area";
import { User, Bot } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

interface MessageViewerProps {
  messages: Message[];
  className?: string;
}

/**
 * MessageViewer Component
 * 
 * Displays chat messages in a conversation bubble format.
 * User messages on the right, assistant messages on the left.
 * 
 * Design: Minimal, white background, ERA Blue accent
 */
export function MessageViewer({ messages, className }: MessageViewerProps) {
  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        No messages in this session
      </div>
    );
  }

  return (
    <ScrollArea className={cn("h-[500px] pr-4", className)}>
      <div className="space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
      </div>
    </ScrollArea>
  );
}

interface MessageBubbleProps {
  message: Message;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
          isUser ? "bg-slate-100" : ""
        )}
        style={!isUser ? { backgroundColor: "#0033A0" } : undefined}
      >
        {isUser ? (
          <User className="h-4 w-4 text-slate-600" />
        ) : (
          <Bot className="h-4 w-4 text-white" />
        )}
      </div>

      {/* Message content */}
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-3",
          isUser
            ? "bg-slate-100 text-slate-800"
            : "bg-white border border-slate-200 text-slate-700"
        )}
      >
        {/* Message text */}
        <div className="text-sm whitespace-pre-wrap leading-relaxed">
          {message.content}
        </div>

        {/* Timestamp */}
        <div
          className={cn(
            "text-xs mt-2",
            isUser ? "text-slate-500 text-right" : "text-slate-400"
          )}
        >
          {formatDate(message.created_at)}
        </div>
      </div>
    </div>
  );
}

export default MessageViewer;
