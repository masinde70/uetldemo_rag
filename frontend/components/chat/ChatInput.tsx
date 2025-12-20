"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Send, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = "Ask a question about UETCL strategy...",
}: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [value]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setValue("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-border-default/50 bg-bg-surface-1/40 backdrop-blur-md p-4">
      <div className="flex items-end gap-3 max-w-4xl mx-auto w-full">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            data-testid="chat-input"
            className={cn(
              "w-full resize-none rounded-xl border border-border-default bg-bg-surface-2/70 px-4 py-3 text-sm text-text-primary backdrop-blur-sm transition-all duration-250",
              "placeholder:text-text-secondary focus:outline-none focus:border-neon-cyan focus:ring-4 focus:ring-neon-cyan/20 focus:shadow-glow-cyan/30",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "min-h-[44px] max-h-[200px] overflow-y-auto"
            )}
          />
        </div>
        <motion.div
          initial={false}
          animate={{ scale: value.trim() ? 1 : 0.95, opacity: value.trim() ? 1 : 0.8 }}
          className="flex-shrink-0"
        >
          <Button
            onClick={handleSend}
            disabled={disabled || !value.trim()}
            size="icon"
            className="h-11 w-11 bg-neon-cyan text-bg-primary hover:bg-cyan-500 hover:shadow-glow-cyan shadow-sm transition-all rounded-xl active:scale-95"
            data-testid="send-button"
          >
            {disabled ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4 font-bold" />
            )}
          </Button>
        </motion.div>
      </div>
      <p className="text-[11px] text-text-secondary mt-2 text-center uppercase tracking-widest opacity-70">
        Press Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}
