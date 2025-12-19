"use client";

import { cn } from "@/lib/utils";
import { User, Bot } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { motion } from "framer-motion";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt?: string;
}

interface ChatBubbleProps {
  message: Message;
}

export function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={cn(
        "flex gap-3 mb-4",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
      data-testid={`message-${message.role}`}
    >
      <div
        className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm",
          isUser
            ? "bg-gradient-to-br from-neon-cyan to-cyan-600 text-bg-primary"
            : "bg-bg-surface-2 border border-border-default text-neon-cyan"
        )}
      >
        {isUser ? (
          <User className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </div>

      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-3 shadow-md transition-all duration-250",
          isUser
            ? "bg-gradient-to-br from-cyan-500 to-cyan-600 text-white shadow-glow-cyan/10"
            : "bg-bg-surface-2 border border-border-default text-text-primary"
        )}
      >
        {isUser ? (
          <div className="text-sm whitespace-pre-wrap leading-relaxed">
            {message.content}
          </div>
        ) : (
          <div className="text-sm leading-relaxed prose prose-sm prose-invert max-w-none prose-p:leading-relaxed prose-headings:font-display prose-headings:text-neon-cyan">
            <ReactMarkdown
              components={{
                // Style tables nicely
                table: ({ children }) => (
                  <table className="min-w-full text-xs border-collapse my-2 bg-bg-surface-1/50 rounded-lg overflow-hidden">
                    {children}
                  </table>
                ),
                th: ({ children }) => (
                  <th className="bg-bg-surface-3 px-3 py-2.5 text-left font-semibold border-b border-border-default text-neon-cyan uppercase tracking-wider text-xs">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-2 py-2 border-b border-border-default/50 text-text-secondary">{children}</td>
                ),
                // Style code blocks
                code: ({ children, className }) => {
                  const isInline = !className;
                  return isInline ? (
                    <code className="bg-bg-surface-3 px-1.5 py-0.5 rounded text-[11px] font-mono text-neon-cyan">
                      {children}
                    </code>
                  ) : (
                    <code className="block bg-bg-primary border border-border-default text-text-primary p-3 rounded-lg text-[11px] font-mono overflow-x-auto shadow-inner">
                      {children}
                    </code>
                  );
                },
                // Style lists
                ul: ({ children }) => (
                  <ul className="list-disc list-outside ml-4 space-y-1 my-2 text-text-secondary">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-outside ml-4 space-y-1 my-2 text-text-secondary">{children}</ol>
                ),
                // Style headings
                h1: ({ children }) => (
                  <h1 className="text-lg font-bold mt-4 mb-2 text-text-primary">{children}</h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-base font-bold mt-4 mb-2 text-text-primary">{children}</h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-sm font-bold mt-3 mb-1 text-text-primary">{children}</h3>
                ),
                // Style blockquotes for citations
                blockquote: ({ children }) => (
                  <blockquote className="border-l-2 border-neon-cyan/50 pl-3 my-2 italic text-text-tertiary bg-neon-cyan/5 py-1 rounded-r">
                    {children}
                  </blockquote>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
        {message.createdAt && (
          <div
            className={cn(
              "text-[11px] mt-2 font-medium uppercase tracking-wide opacity-70",
              isUser ? "text-cyan-100" : "text-text-tertiary"
            )}
          >
            {new Date(message.createdAt).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        )}
      </div>
    </motion.div>
  );
}
