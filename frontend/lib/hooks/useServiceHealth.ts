/**
 * React hook for monitoring backend service health.
 *
 * Polls the /api/health/detailed endpoint and provides
 * service status and capability flags for graceful degradation.
 */

import { useState, useEffect, useCallback, useRef } from "react";

export type ServiceStatus = "healthy" | "degraded" | "unhealthy";

export interface ServiceInfo {
  status: ServiceStatus;
  latency_ms: number | null;
  message: string | null;
}

export interface SystemCapabilities {
  chat: boolean;
  streaming: boolean;
  session_history: boolean;
  document_retrieval: boolean;
  analytics: boolean;
  admin: boolean;
  file_upload: boolean;
}

export interface HealthStatus {
  status: ServiceStatus;
  timestamp: string;
  services: {
    database: ServiceInfo;
    qdrant: ServiceInfo;
    openai: ServiceInfo;
  };
  capabilities: SystemCapabilities;
}

export interface UseServiceHealthOptions {
  /** Polling interval in ms (default: 30000) */
  pollInterval?: number;
  /** Enable polling (default: true) */
  enabled?: boolean;
  /** Called when health status changes */
  onStatusChange?: (status: HealthStatus) => void;
}

export interface UseServiceHealthResult {
  /** Current health status */
  health: HealthStatus | null;
  /** Whether currently fetching health */
  isLoading: boolean;
  /** Last error if any */
  error: Error | null;
  /** Whether system is online */
  isOnline: boolean;
  /** Whether system is fully operational */
  isHealthy: boolean;
  /** Whether system is in degraded mode */
  isDegraded: boolean;
  /** Manually refresh health status */
  refresh: () => Promise<void>;
}

const DEFAULT_HEALTH: HealthStatus = {
  status: "unhealthy",
  timestamp: new Date().toISOString(),
  services: {
    database: { status: "unhealthy", latency_ms: null, message: "Unknown" },
    qdrant: { status: "unhealthy", latency_ms: null, message: "Unknown" },
    openai: { status: "unhealthy", latency_ms: null, message: "Unknown" },
  },
  capabilities: {
    chat: false,
    streaming: false,
    session_history: false,
    document_retrieval: false,
    analytics: false,
    admin: false,
    file_upload: false,
  },
};

/**
 * Hook for monitoring service health and determining available capabilities.
 *
 * @example
 * ```tsx
 * const { health, isHealthy, isDegraded, refresh } = useServiceHealth({
 *   pollInterval: 30000,
 *   onStatusChange: (status) => {
 *     if (status.status === "unhealthy") {
 *       toast.error("Some services are unavailable");
 *     }
 *   },
 * });
 *
 * // Check if chat is available before sending
 * if (!health?.capabilities.chat) {
 *   return <OfflineMessage />;
 * }
 * ```
 */
export function useServiceHealth(
  options: UseServiceHealthOptions = {}
): UseServiceHealthResult {
  const { pollInterval = 30000, enabled = true, onStatusChange } = options;

  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [isOnline, setIsOnline] = useState(
    typeof navigator !== "undefined" ? navigator.onLine : true
  );

  const previousStatusRef = useRef<ServiceStatus | null>(null);
  const onStatusChangeRef = useRef(onStatusChange);
  onStatusChangeRef.current = onStatusChange;

  const fetchHealth = useCallback(async () => {
    if (!isOnline) {
      setHealth({
        ...DEFAULT_HEALTH,
        timestamp: new Date().toISOString(),
      });
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/health/detailed", {
        signal: AbortSignal.timeout(10000),
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }

      const data: HealthStatus = await response.json();
      setHealth(data);

      // Notify on status change
      if (
        previousStatusRef.current !== null &&
        previousStatusRef.current !== data.status &&
        onStatusChangeRef.current
      ) {
        onStatusChangeRef.current(data);
      }
      previousStatusRef.current = data.status;
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Unknown error");
      setError(error);

      // Set offline health status
      setHealth({
        ...DEFAULT_HEALTH,
        timestamp: new Date().toISOString(),
      });
    } finally {
      setIsLoading(false);
    }
  }, [isOnline]);

  // Track browser online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  // Initial fetch and polling
  useEffect(() => {
    if (!enabled) return;

    // Initial fetch
    fetchHealth();

    // Set up polling
    const intervalId = setInterval(fetchHealth, pollInterval);

    return () => clearInterval(intervalId);
  }, [enabled, pollInterval, fetchHealth]);

  // Refresh when coming back online
  useEffect(() => {
    if (isOnline) {
      fetchHealth();
    }
  }, [isOnline, fetchHealth]);

  const isHealthy = health?.status === "healthy";
  const isDegraded = health?.status === "degraded";

  return {
    health,
    isLoading,
    error,
    isOnline,
    isHealthy,
    isDegraded,
    refresh: fetchHealth,
  };
}

export default useServiceHealth;
