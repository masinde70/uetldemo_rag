/**
 * API Client for SISUiQ Admin Dashboard
 *
 * Provides typed fetch helpers with JWT authentication.
 * Token is stored in localStorage under key: "token"
 * 
 * Note: In development, API calls go through Next.js API routes
 * which proxy to the backend with the admin token.
 */

// Use relative paths to go through Next.js API routes (handles auth)
const API_BASE_URL = "";

// --- Types ---

export interface ApiResponse<T> {
  data: T;
  count?: number;
}

export interface ApiError {
  detail: string;
  status: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  created_at: string;
  session_count: number;
}

export interface Session {
  id: string;
  user_email: string;
  user_name: string;
  mode: string;
  title: string | null;
  message_count: number;
  created_at: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface Document {
  id: string;
  name: string;
  type: string;
  source: string;
  file_path: string;
  chunk_count: number;
  created_at: string;
}

export interface AnalyticsSnapshot {
  id: string;
  dataset_name: string;
  row_count: number | null;
  file_path: string | null;
  created_at: string;
  summary: Record<string, unknown>;
}

export interface Stats {
  users: number;
  sessions: number;
  messages: number;
  documents: number;
  chunks: number;
  analytics_snapshots: number;
}

// --- Auth Helpers ---

/**
 * Get the auth token from localStorage
 */
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

/**
 * Set the auth token in localStorage
 */
export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("token", token);
}

/**
 * Remove the auth token from localStorage
 */
export function clearToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("token");
}

// --- Request Helpers ---

/**
 * Build headers with optional auth token
 */
function buildHeaders(includeAuth: boolean = true): HeadersInit {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (includeAuth) {
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  return headers;
}

/**
 * Handle API response and errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = "An error occurred";
    try {
      const errorData = await response.json();
      detail = errorData.detail || detail;
    } catch {
      detail = response.statusText;
    }

    const error: ApiError = {
      detail,
      status: response.status,
    };
    throw error;
  }

  return response.json();
}

// --- API Methods ---

/**
 * GET request with auth
 */
export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "GET",
    headers: buildHeaders(),
  });

  return handleResponse<T>(response);
}

/**
 * POST request with auth
 */
export async function apiPost<T, D = unknown>(path: string, data?: D): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: buildHeaders(),
    body: data ? JSON.stringify(data) : undefined,
  });

  return handleResponse<T>(response);
}

/**
 * PUT request with auth
 */
export async function apiPut<T, D = unknown>(path: string, data?: D): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "PUT",
    headers: buildHeaders(),
    body: data ? JSON.stringify(data) : undefined,
  });

  return handleResponse<T>(response);
}

/**
 * DELETE request with auth
 */
export async function apiDelete<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "DELETE",
    headers: buildHeaders(),
  });

  return handleResponse<T>(response);
}

// --- Admin API Functions ---

/**
 * Fetch admin stats
 */
export async function fetchStats(): Promise<Stats> {
  return apiGet<Stats>("/api/admin/stats");
}

/**
 * Fetch all users with pagination
 */
export async function fetchUsers(
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponse<User[]>> {
  return apiGet<ApiResponse<User[]>>(
    `/api/admin/users?limit=${limit}&offset=${offset}`
  );
}

/**
 * Fetch all sessions with pagination
 */
export async function fetchSessions(
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponse<Session[]>> {
  return apiGet<ApiResponse<Session[]>>(
    `/api/admin/sessions?limit=${limit}&offset=${offset}`
  );
}

/**
 * Fetch messages for a specific session
 */
export async function fetchSessionMessages(
  sessionId: string
): Promise<ApiResponse<Message[]>> {
  return apiGet<ApiResponse<Message[]>>(
    `/api/admin/sessions/${sessionId}/messages`
  );
}

/**
 * Fetch all documents with pagination
 */
export async function fetchDocuments(
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponse<Document[]>> {
  return apiGet<ApiResponse<Document[]>>(
    `/api/admin/documents?limit=${limit}&offset=${offset}`
  );
}

/**
 * Fetch all analytics snapshots with pagination
 */
export async function fetchAnalytics(
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponse<AnalyticsSnapshot[]>> {
  return apiGet<ApiResponse<AnalyticsSnapshot[]>>(
    `/api/admin/analytics?limit=${limit}&offset=${offset}`
  );
}

// --- Utility Functions ---

/**
 * Format ISO date string to readable format
 */
export function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Get mode display name with proper capitalization
 */
export function getModeDisplayName(mode: string): string {
  const modeNames: Record<string, string> = {
    strategy_qa: "Strategy Q&A",
    actions: "Actions",
    analytics: "Analytics",
    regulatory: "Regulatory",
  };
  return modeNames[mode] || mode;
}

/**
 * Get badge color class for document type
 */
export function getTypeColor(type: string): string {
  const colors: Record<string, string> = {
    strategy: "bg-blue-100 text-blue-700",
    regulation: "bg-purple-100 text-purple-700",
    other: "bg-slate-100 text-slate-700",
  };
  return colors[type] || colors.other;
}

/**
 * Get badge color class for document source
 */
export function getSourceColor(source: string): string {
  const colors: Record<string, string> = {
    UETCL: "bg-green-100 text-green-700",
    ERA: "bg-orange-100 text-orange-700",
    other: "bg-slate-100 text-slate-700",
  };
  return colors[source] || colors.other;
}

/**
 * Get badge color class for user role
 */
export function getRoleColor(role: string): string {
  const colors: Record<string, string> = {
    admin: "bg-red-100 text-red-700",
    user: "bg-blue-100 text-blue-700",
  };
  return colors[role] || colors.user;
}
