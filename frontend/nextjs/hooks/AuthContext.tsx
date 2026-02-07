"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";

interface AuthContextType {
  isAuthenticated: boolean;
  username: string | null;
  authEnabled: boolean | null; // null = still checking
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  token: string | null;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  username: null,
  authEnabled: null,
  login: async () => ({ success: false }),
  logout: async () => {},
  token: null,
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [authEnabled, setAuthEnabled] = useState<boolean | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // Check if auth is enabled and if user is already logged in
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // First check if auth is enabled on the server
        const statusRes = await fetch("/api/auth/status");
        const statusData = await statusRes.json();

        if (!statusData.auth_enabled) {
          // Auth is disabled, everyone is allowed
          setAuthEnabled(false);
          setIsAuthenticated(true);
          setUsername("anonymous");
          return;
        }

        setAuthEnabled(true);

        // Auth is enabled - check if we have a valid token
        const savedToken = localStorage.getItem("auth_token");
        if (savedToken) {
          const meRes = await fetch("/api/auth/me", {
            headers: { Authorization: `Bearer ${savedToken}` },
          });
          if (meRes.ok) {
            const meData = await meRes.json();
            setIsAuthenticated(true);
            setUsername(meData.username);
            setToken(savedToken);
            return;
          }
          // Token is invalid, clear it
          localStorage.removeItem("auth_token");
        }

        setIsAuthenticated(false);
      } catch (err) {
        console.error("Auth check failed:", err);
        // If we can't reach the server, assume auth is disabled for local dev
        setAuthEnabled(false);
        setIsAuthenticated(true);
        setUsername("anonymous");
      }
    };

    checkAuth();
  }, []);

  const login = useCallback(async (usr: string, pwd: string) => {
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: usr, password: pwd }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        return { success: false, error: data.detail || "Login failed" };
      }

      const data = await res.json();
      localStorage.setItem("auth_token", data.token);
      setToken(data.token);
      setIsAuthenticated(true);
      setUsername(data.username);
      return { success: true };
    } catch (err) {
      return { success: false, error: "Network error" };
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await fetch("/api/auth/logout", { method: "POST" });
    } catch {
      // ignore
    }
    localStorage.removeItem("auth_token");
    setToken(null);
    setIsAuthenticated(false);
    setUsername(null);
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, username, authEnabled, login, logout, token }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
