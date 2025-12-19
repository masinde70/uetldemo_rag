"use client";

import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, WifiOff, RefreshCw, X, CheckCircle } from "lucide-react";
import { useState, useCallback } from "react";
import { HealthStatus, ServiceStatus } from "@/lib/hooks";

interface StatusBannerProps {
  health: HealthStatus | null;
  isOnline: boolean;
  isLoading: boolean;
  onRefresh: () => void;
}

/**
 * Status banner that displays system health warnings.
 *
 * Shows different messages for:
 * - Offline mode (no network)
 * - Degraded mode (some services slow/unavailable)
 * - Unhealthy mode (critical services down)
 */
export function StatusBanner({
  health,
  isOnline,
  isLoading,
  onRefresh,
}: StatusBannerProps) {
  const [dismissed, setDismissed] = useState(false);

  const handleDismiss = useCallback(() => {
    setDismissed(true);
    // Reset dismiss after 5 minutes
    setTimeout(() => setDismissed(false), 5 * 60 * 1000);
  }, []);

  // Don't show if healthy or dismissed
  if (
    dismissed ||
    (isOnline && health?.status === "healthy")
  ) {
    return null;
  }

  // Determine banner content
  let icon: React.ReactNode;
  let title: string;
  let message: string;
  let bgColor: string;
  let borderColor: string;

  if (!isOnline) {
    icon = <WifiOff className="w-5 h-5" />;
    title = "You're offline";
    message = "Check your internet connection. Some features may be unavailable.";
    bgColor = "bg-red-500/10";
    borderColor = "border-red-500/30";
  } else if (health?.status === "unhealthy") {
    icon = <AlertTriangle className="w-5 h-5" />;
    title = "Service disruption";
    message = getUnhealthyMessage(health);
    bgColor = "bg-red-500/10";
    borderColor = "border-red-500/30";
  } else if (health?.status === "degraded") {
    icon = <AlertTriangle className="w-5 h-5" />;
    title = "Degraded performance";
    message = getDegradedMessage(health);
    bgColor = "bg-yellow-500/10";
    borderColor = "border-yellow-500/30";
  } else {
    // Unknown state, show warning
    icon = <AlertTriangle className="w-5 h-5" />;
    title = "Checking services...";
    message = "Verifying system health.";
    bgColor = "bg-yellow-500/10";
    borderColor = "border-yellow-500/30";
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className={`${bgColor} ${borderColor} border-b px-4 py-2`}
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-text-secondary">{icon}</span>
            <div>
              <span className="font-medium text-sm text-text-primary">
                {title}
              </span>
              <span className="text-text-secondary text-sm ml-2">
                {message}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-1.5 rounded-md hover:bg-white/10 transition-colors text-text-secondary"
              title="Refresh status"
            >
              <RefreshCw
                className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`}
              />
            </button>
            <button
              onClick={handleDismiss}
              className="p-1.5 rounded-md hover:bg-white/10 transition-colors text-text-secondary"
              title="Dismiss"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

function getUnhealthyMessage(health: HealthStatus): string {
  const unhealthyServices: string[] = [];

  if (health.services.database.status === "unhealthy") {
    unhealthyServices.push("database");
  }
  if (health.services.qdrant.status === "unhealthy") {
    unhealthyServices.push("search");
  }
  if (health.services.openai.status === "unhealthy") {
    unhealthyServices.push("AI");
  }

  if (unhealthyServices.length === 0) {
    return "Some services are experiencing issues.";
  }

  const services = unhealthyServices.join(", ");
  const isPlural = unhealthyServices.length > 1;

  return `The ${services} service${isPlural ? "s are" : " is"} unavailable. Some features won't work.`;
}

function getDegradedMessage(health: HealthStatus): string {
  const degradedServices: string[] = [];

  if (health.services.database.status === "degraded") {
    degradedServices.push("database");
  }
  if (health.services.qdrant.status === "degraded") {
    degradedServices.push("search");
  }
  if (health.services.openai.status === "degraded") {
    degradedServices.push("AI");
  }

  if (degradedServices.length === 0) {
    return "Some services are running slowly.";
  }

  const services = degradedServices.join(", ");
  const isPlural = degradedServices.length > 1;

  return `The ${services} service${isPlural ? "s are" : " is"} running slowly. Responses may be delayed.`;
}

/**
 * Compact status indicator for the topbar.
 */
export function StatusIndicator({
  health,
  isOnline,
}: {
  health: HealthStatus | null;
  isOnline: boolean;
}) {
  if (!isOnline) {
    return (
      <div className="flex items-center gap-1.5 text-red-400 text-xs">
        <WifiOff className="w-3.5 h-3.5" />
        <span>Offline</span>
      </div>
    );
  }

  if (!health) {
    return null;
  }

  if (health.status === "healthy") {
    return (
      <div className="flex items-center gap-1.5 text-green-400 text-xs">
        <CheckCircle className="w-3.5 h-3.5" />
        <span>All systems operational</span>
      </div>
    );
  }

  if (health.status === "degraded") {
    return (
      <div className="flex items-center gap-1.5 text-yellow-400 text-xs">
        <AlertTriangle className="w-3.5 h-3.5" />
        <span>Degraded</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5 text-red-400 text-xs">
      <AlertTriangle className="w-3.5 h-3.5" />
      <span>Issues detected</span>
    </div>
  );
}

export default StatusBanner;
