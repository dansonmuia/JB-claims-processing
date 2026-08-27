export const CLAIM_TYPES = ["MOTOR", "HEALTH", "TRAVEL", "PROPERTY", "OTHER"] as const;
export type ClaimType = (typeof CLAIM_TYPES)[number];

export const CLAIM_STATUSES = [
  "SUBMITTED",
  "UNDER_REVIEW",
  "APPROVED",
  "REJECTED",
  "PAID",
] as const;
export type ClaimStatus = (typeof CLAIM_STATUSES)[number];

// Mirrors the transition rules enforced server-side in Backend/app/claims/routes.py
export function nextAllowedStatuses(status: ClaimStatus): ClaimStatus[] {
  switch (status) {
    case "SUBMITTED":
      return ["UNDER_REVIEW"];
    case "UNDER_REVIEW":
      return ["APPROVED", "REJECTED"];
    case "APPROVED":
    case "REJECTED":
      return ["PAID"];
    case "PAID":
      return [];
    default:
      return [];
  }
}

export interface Claim {
  id: string;
  claim_number: string;
  policy_id: string;
  claim_type: ClaimType;
  claim_amount: number;
  incident_date: string;
  description: string | null;
  status: ClaimStatus;
}

export interface ClaimCreateInput {
  claim_number: string;
  policy_id: string;
  claim_type: ClaimType;
  claim_amount: number;
  incident_date: string;
  description?: string | null;
}

export interface ClaimUpdateInput {
  claim_amount: number;
  incident_date: string;
  description?: string | null;
  status: ClaimStatus;
}

export interface PaginatedClaims {
  items: Claim[];
  count: number;
  offset: number;
  limit: number;
}

export interface AdminMinimal {
  id: string;
  name: string;
  email: string;
  msisdn: string;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  admin: AdminMinimal;
}
