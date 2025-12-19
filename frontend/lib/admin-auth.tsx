"use client";

/**
 * @deprecated Use the new auth module instead: import { useAuth, AuthProvider } from "@/lib/auth"
 * 
 * This module provides backwards compatibility for the legacy admin auth system.
 */

export { 
  useAdminAuth, 
  AdminAuthProvider,
  useAuth,
  AuthProvider,
} from "./auth";
