import type {
  Claim,
  ClaimCreateInput,
  ClaimUpdateInput,
  LoginResponse,
  PaginatedClaims,
} from "./types";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api").replace(/\/$/, "");

const TOKEN_STORAGE_KEY = "jb_claims_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setToken(token: string): void {
  window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function extractErrorMessage(body: unknown, fallback: string): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((item) => (typeof item === "object" && item && "msg" in item ? String((item as { msg: unknown }).msg) : String(item)))
        .join(", ");
    }
  }
  return fallback;
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (response.status === 204) {
    return undefined as T;
  }

  const body = await response.json().catch(() => undefined);

  if (!response.ok) {
    if (response.status === 401) clearToken();
    throw new ApiError(extractErrorMessage(body, `Request failed with status ${response.status}`), response.status);
  }

  return body as T;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  return apiFetch<LoginResponse>("/auth/login-for-token-no-2fa", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export interface ListClaimsParams {
  offset?: number;
  limit?: number;
  claim_number?: string;
  policy_id?: string;
}

export async function listClaims(params: ListClaimsParams = {}): Promise<PaginatedClaims> {
  const query = new URLSearchParams();
  if (params.offset !== undefined) query.set("offset", String(params.offset));
  if (params.limit !== undefined) query.set("limit", String(params.limit));
  if (params.claim_number) query.set("claim_number", params.claim_number);
  if (params.policy_id) query.set("policy_id", params.policy_id);

  const qs = query.toString();
  return apiFetch<PaginatedClaims>(`/claims/${qs ? `?${qs}` : ""}`);
}

export async function getClaim(id: string): Promise<Claim> {
  return apiFetch<Claim>(`/claims/${id}`);
}

export async function createClaim(input: ClaimCreateInput): Promise<Claim> {
  return apiFetch<Claim>("/claims/", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function updateClaim(id: string, input: ClaimUpdateInput): Promise<Claim> {
  return apiFetch<Claim>(`/claims/${id}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}
