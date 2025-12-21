"use client";

import { cn } from "@/lib/utils";
import {
  MessageSquare,
  ListTodo,
  BarChart3,
  Scale,
  X,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export type ChatMode = "strategy_qa" | "actions" | "analytics" | "regulatory";

interface SidebarProps {
  selectedMode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

const modes = [
  {
    id: "strategy_qa" as ChatMode,
    label: "Strategy Q&A",
    description: "Ask about UETCL strategic plans",
    icon: MessageSquare,
  },
  {
    id: "actions" as ChatMode,
    label: "Action Planner",
    description: "Get actionable recommendations",
    icon: ListTodo,
  },
  {
    id: "analytics" as ChatMode,
    label: "Analytics + Strategy",
    description: "Combine data with strategy",
    icon: BarChart3,
  },
  {
    id: "regulatory" as ChatMode,
    label: "Regulatory Advisor",
    description: "ERA compliance guidance",
    icon: Scale,
  },
];

export function Sidebar({ selectedMode, onModeChange, isOpen = true, onClose }: SidebarProps) {
  const handleModeSelect = (mode: ChatMode) => {
    onModeChange(mode);
    // Close sidebar on mobile after selection
    if (onClose && window.innerWidth < 768) {
      onClose();
    }
  };

  return (
    <>
      {/* Mobile overlay */}
      <AnimatePresence>
        {isOpen && onClose && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 md:hidden"
            onClick={onClose}
          />
        )}
      </AnimatePresence>

      <aside
        className={cn(
          "w-64 border-r border-border-default/50 bg-bg-surface-1/80 backdrop-blur-md flex flex-col flex-shrink-0",
          "fixed md:relative inset-y-0 left-0 z-50 md:z-auto",
          "transform transition-transform duration-300 ease-in-out md:transform-none",
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        )}
        data-testid="sidebar"
      >
        <div className="p-4 border-b border-border-default/50 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider font-display">
            Modes
          </h2>
          {/* Mobile close button */}
          {onClose && (
            <button
              onClick={onClose}
              className="md:hidden p-1 rounded-lg hover:bg-bg-surface-2 text-text-secondary"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>
        <nav className="flex-1 p-2 space-y-1 overflow-y-auto min-h-0 scrollbar-thin scrollbar-thumb-border-default scrollbar-track-transparent">
          {modes.map((mode) => {
            const Icon = mode.icon;
            const isSelected = selectedMode === mode.id;

            return (
              <motion.button
                key={mode.id}
                whileHover={{ scale: 1.02, x: 4 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleModeSelect(mode.id)}
                data-testid={`mode-${mode.id}`}
                className={cn(
                  "w-full flex items-start gap-3 p-3 rounded-lg text-left transition-all duration-200 relative",
                  isSelected
                    ? "bg-primary/15 text-primary border border-primary/40 dark:shadow-glow-cyan before:absolute before:left-0 before:top-2 before:bottom-2 before:w-1 before:bg-primary before:rounded-full"
                    : "hover:bg-bg-surface-2 text-text-secondary hover:text-text-primary hover:border-border-default border border-transparent"
                )}
              >
                <Icon
                  className={cn(
                    "h-5 w-5 mt-0.5 flex-shrink-0",
                    isSelected ? "text-primary" : "text-text-tertiary"
                  )}
                />
                <div className="flex flex-col">
                  <span className="font-medium text-sm">{mode.label}</span>
                  <span
                    className={cn(
                      "text-xs mt-0.5",
                      isSelected ? "text-primary/80" : "text-text-tertiary"
                    )}
                  >
                    {mode.description}
                  </span>
                </div>
              </motion.button>
            );
          })}
        </nav>
        <div className="p-4 border-t border-border-default/50">
          <p className="text-xs text-text-tertiary text-center">
            SISUiQ v0.1.0
          </p>
        </div>
      </aside>
    </>
  );
}
