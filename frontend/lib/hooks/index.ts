/**
 * Re-export all hooks for convenient imports.
 *
 * @example
 * import { useStreamingChat, useServiceHealth } from "@/lib/hooks";
 */

export { useStreamingChat } from "./useStreamingChat";
export type {
  StreamingMessage,
  StreamingChatOptions,
  StreamingChatResult,
} from "./useStreamingChat";

export { useServiceHealth } from "./useServiceHealth";
export type {
  ServiceStatus,
  ServiceInfo,
  SystemCapabilities,
  HealthStatus,
  UseServiceHealthOptions,
  UseServiceHealthResult,
} from "./useServiceHealth";
