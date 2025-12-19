"use client";

import { useState, useEffect, createContext, useContext, ReactNode, useCallback } from "react";

/**
 * Production-ready authentication context using HttpOnly cookies.
 * 
 * Features:
 * - No localStorage (HttpOnly cookies are secure)
 * - Automatic token refresh
 * - Per-user authentication with email/password
 * - CSRF protection via SameSite cookies
 */

// --- Types ---

interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "user";
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
}

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<boolean>;
}

interface LoginResponse {
  message: string;
  user: User;
  expires_in: number;
}

// --- Context ---

const AuthContext = createContext<AuthContextValue>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  isAdmin: false,
  login: async () => ({ success: false, error: "Not initialized" }),
  logout: async () => {},
  refreshAuth: async () => false,
});

export function useAuth() {
  return useContext(AuthContext);
}

// Legacy alias for backwards compatibility
export function useAdminAuth() {
  const auth = useAuth();
  return {
    isAuthenticated: auth.isAuthenticated && auth.isAdmin,
    isLoading: auth.isLoading,
    login: async (password: string) => {
      // Legacy token-based login - try with default admin email
      const result = await auth.login("admin@sisuiq.local", password);
      return result.success;
    },
    logout: auth.logout,
    token: null, // No longer exposed
  };
}

// --- Provider ---

const TOKEN_REFRESH_INTERVAL = 10 * 60 * 1000; // 10 minutes (before 15 min expiry)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = user !== null;
  const isAdmin = user?.role === "admin";

  // Check authentication status on mount
  const checkAuth = useCallback(async (): Promise<boolean> => {
    try {
      const res = await fetch("/api/auth/me", {
        credentials: "include", // Include HttpOnly cookies
      });
      
      if (res.ok) {
        const userData: User = await res.json();
        setUser(userData);
        return true;
      } else {
        setUser(null);
        return false;
      }
    } catch {
      setUser(null);
      return false;
    }
  }, []);

  // Refresh the access token
  const refreshAuth = useCallback(async (): Promise<boolean> => {
    try {
      const res = await fetch("/api/auth/refresh", {
        method: "POST",
        credentials: "include",
      });
      
      if (res.ok) {
        const data: LoginResponse = await res.json();
        setUser(data.user);
        return true;
      } else {
        setUser(null);
        return false;
      }
    } catch {
      setUser(null);
      return false;
    }
  }, []);

  // Login with email and password
  const login = useCallback(async (
    email: string, 
    password: string
  ): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);
    
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // Accept HttpOnly cookies
        body: JSON.stringify({ email, password }),
      });
      
      if (res.ok) {
        const data: LoginResponse = await res.json();
        setUser(data.user);
        setIsLoading(false);
        return { success: true };
      } else {
        const error = await res.json();
        setIsLoading(false);
        return { 
          success: false, 
          error: error.detail || "Login failed" 
        };
      }
    } catch (err) {
      setIsLoading(false);
      return { 
        success: false, 
        error: "Network error. Please try again." 
      };
    }
  }, []);

  // Logout
  const logout = useCallback(async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch {
      // Ignore errors - we're logging out anyway
    }
    setUser(null);
  }, []);

  // Initial auth check
  useEffect(() => {
    checkAuth().finally(() => setIsLoading(false));
  }, [checkAuth]);

  // Set up token refresh interval
  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(() => {
      refreshAuth();
    }, TOKEN_REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, [isAuthenticated, refreshAuth]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        isAdmin,
        login,
        logout,
        refreshAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// --- Legacy Provider Alias ---

export function AdminAuthProvider({ children }: { children: ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}
