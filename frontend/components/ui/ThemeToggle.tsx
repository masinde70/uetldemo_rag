"use client";

import * as React from "react";
import { Moon, Sun, Monitor } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  // Avoid hydration mismatch
  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // Placeholder to prevent layout shift
    return (
      <div className="flex items-center gap-1 p-1 rounded-lg bg-muted">
        <div className="h-8 w-8" />
        <div className="h-8 w-8" />
        <div className="h-8 w-8" />
      </div>
    );
  }

  const themes = [
    { value: "light", icon: Sun, label: "Light" },
    { value: "dark", icon: Moon, label: "Dark" },
    { value: "system", icon: Monitor, label: "System" },
  ];

  return (
    <div className="flex items-center gap-1 p-1 rounded-lg bg-muted/50 border border-border">
      {themes.map(({ value, icon: Icon, label }) => (
        <Button
          key={value}
          variant="ghost"
          size="sm"
          onClick={() => setTheme(value)}
          className={cn(
            "h-8 w-8 p-0 transition-all",
            theme === value
              ? "bg-background shadow-sm text-primary"
              : "text-muted-foreground hover:text-foreground"
          )}
          aria-label={`Switch to ${label} theme`}
          title={label}
        >
          <Icon className="h-4 w-4" />
        </Button>
      ))}
    </div>
  );
}

/**
 * Compact version for tight spaces (just shows current theme icon)
 */
export function ThemeToggleCompact() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="h-9 w-9" />;
  }

  const cycleTheme = () => {
    if (theme === "light") setTheme("dark");
    else if (theme === "dark") setTheme("system");
    else setTheme("light");
  };

  const Icon = resolvedTheme === "dark" ? Moon : Sun;
  const isSystem = theme === "system";

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={cycleTheme}
      className="h-9 w-9 p-0 relative"
      aria-label="Toggle theme"
      title={`Current: ${theme} (click to cycle)`}
    >
      <Icon className="h-4 w-4" />
      {isSystem && (
        <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 bg-primary rounded-full" />
      )}
    </Button>
  );
}
