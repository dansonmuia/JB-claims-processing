"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { clearToken, getToken, login as apiLogin, setToken } from "./api";
import type { AdminMinimal } from "./types";

const ADMIN_STORAGE_KEY = "jb_claims_admin";

interface AuthContextValue {
  admin: AdminMinimal | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [admin, setAdmin] = useState<AdminMinimal | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    const storedAdmin = window.localStorage.getItem(ADMIN_STORAGE_KEY);
    if (token && storedAdmin) {
      try {
        // eslint-disable-next-line react-hooks/set-state-in-effect -- hydrating from localStorage on mount
        setAdmin(JSON.parse(storedAdmin) as AdminMinimal);
      } catch {
        window.localStorage.removeItem(ADMIN_STORAGE_KEY);
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const response = await apiLogin(email, password);
    setToken(response.access_token);
    window.localStorage.setItem(ADMIN_STORAGE_KEY, JSON.stringify(response.admin));
    setAdmin(response.admin);
  }, []);

  const logout = useCallback(() => {
    clearToken();
    window.localStorage.removeItem(ADMIN_STORAGE_KEY);
    setAdmin(null);
  }, []);

  const value = useMemo(
    () => ({ admin, isLoading, isAuthenticated: admin !== null, login, logout }),
    [admin, isLoading, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
