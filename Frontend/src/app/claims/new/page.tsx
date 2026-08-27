"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { useRouter } from "next/navigation";

import AuthGuard from "@/components/AuthGuard";
import { ApiError, createClaim } from "@/lib/api";
import { CLAIM_TYPES, type ClaimType } from "@/lib/types";

function NewClaimInner() {
  const router = useRouter();

  const [claimNumber, setClaimNumber] = useState("");
  const [policyId, setPolicyId] = useState("");
  const [claimType, setClaimType] = useState<ClaimType>("MOTOR");
  const [claimAmount, setClaimAmount] = useState("");
  const [incidentDate, setIncidentDate] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const claim = await createClaim({
        claim_number: claimNumber.trim(),
        policy_id: policyId.trim(),
        claim_type: claimType,
        claim_amount: Number(claimAmount),
        incident_date: incidentDate,
        description: description.trim() || null,
      });
      router.replace(`/claims/${claim.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create claim.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-lg">
      <h1 className="mb-6 text-2xl font-semibold text-slate-900">New Claim</h1>

      <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border border-slate-200 bg-white p-6">
        {error && <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

        <label className="block text-sm">
          <span className="mb-1 block text-slate-600">Claim number</span>
          <input
            required
            value={claimNumber}
            onChange={(e) => setClaimNumber(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
            placeholder="CLM-0001"
          />
        </label>

        <label className="block text-sm">
          <span className="mb-1 block text-slate-600">Policy ID</span>
          <input
            required
            value={policyId}
            onChange={(e) => setPolicyId(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
            placeholder="UUID of an existing policy"
          />
        </label>

        <label className="block text-sm">
          <span className="mb-1 block text-slate-600">Claim type</span>
          <select
            value={claimType}
            onChange={(e) => setClaimType(e.target.value as ClaimType)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
          >
            {CLAIM_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>

        <label className="block text-sm">
          <span className="mb-1 block text-slate-600">Claim amount</span>
          <input
            type="number"
            required
            min="0"
            step="0.01"
            value={claimAmount}
            onChange={(e) => setClaimAmount(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
          />
        </label>

        <label className="block text-sm">
          <span className="mb-1 block text-slate-600">Incident date</span>
          <input
            type="date"
            required
            value={incidentDate}
            onChange={(e) => setIncidentDate(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
          />
        </label>

        <label className="block text-sm">
          <span className="mb-1 block text-slate-600">Description (optional)</span>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
          />
        </label>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {submitting ? "Creating..." : "Create claim"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function NewClaimPage() {
  return (
    <AuthGuard>
      <NewClaimInner />
    </AuthGuard>
  );
}
