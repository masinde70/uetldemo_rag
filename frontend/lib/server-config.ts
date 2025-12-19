/**
 * Server-side configuration helper.
 * 
 * These functions read environment variables at runtime,
 * which is necessary for Docker containers where env vars
 * are set when the container starts, not when the image is built.
 */

export function getBackendUrl(): string {
  return process.env.BACKEND_URL || "http://localhost:8000";
}

export function getAdminToken(): string {
  return process.env.ADMIN_TOKEN || "demo-admin-token-change-me";
}

/**
 * Create headers for admin API requests
 */
export function getAdminHeaders(): HeadersInit {
  return {
    "X-Admin-Token": getAdminToken(),
    "Content-Type": "application/json",
  };
}
