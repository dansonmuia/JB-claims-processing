"use client";

import { use, useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";

import AuthGuard from "@/components/AuthGuard";
import StatusBadge from "@/components/StatusBadge";
import { ApiError, getClaim, updateClaim } from "@/lib/api";
import { nextAllowedStatuses, type Claim } from "@/lib/types";

function toDateInputValue(isoString: string): string {
  return isoString.slice(0, 10);
}

function ClaimDetailInner({ claimId }: { claimId: string }) {
  const [claim, setClaim] = useState<Claim | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [claimAmount, setClaimAmount] = useState("");
  const [incidentDate, setIncidentDate] = useState("");
  const [description, setDescription] = useState("");

  const [saveError, setSaveError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [pendingStatus, setPendingStatus] = useState<string | null>(null);

  const loadClaim = useCallback(async () => {
    setIsLoading(true);
    setLoadError(null);
    try {
      const result = await getClaim(claimId);
      setClaim(result);
      setClaimAmount(String(result.claim_amount));
      setIncidentDate(toDateInputValue(result.incident_date));
      setDescription(result.description ?? "");
    } catch (err) {
      setLoadError(err instanceof ApiError ? err.message : "Failed to load claim.");
    } finally {
      setIsLoading(false);
    }
  }, [claimId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetching the claim for this route on mount
    loadClaim();
  }, [loadClaim]);

  const handleSaveDetails = async (event: FormEvent) => {
    event.preventDefault();
    if (!claim) return;
    setSaveError(null);
    setIsSaving(true);
    try {
      const updated = await updateClaim(claim.id, {
        claim_amount: Number(claimAmount),
        incident_date: incidentDate,
        description: description.trim() || null,
        status: claim.status,
      });
      setClaim(updated);
    } catch (err) {
      setSaveError(err instanceof ApiError ? err.message : "Failed to update claim.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleStatusChange = async (status: string) => {
    if (!claim) return;
    setSaveError(null);
    setPendingStatus(status);
    try {
      const updated = await updateClaim(claim.id, {
        claim_amount: Number(claimAmount),
        incident_date: incidentDate,
        description: description.trim() || null,
        status: status as Claim["status"],
      });
      setClaim(updated);
    } catch (err) {
      setSaveError(err instanceof ApiError ? err.message : "Failed to update status.");
    } finally {
      setPendingStatus(null);
    }
  };

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading claim...</p>;
  }

  if (loadError || !claim) {
    return <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{loadError ?? "Claim not found."}</div>;
  }

  const upcomingStatuses = nextAllowedStatuses(claim.status);

  return (
    <div className="mx-auto w-full max-w-2xl">
      <Link href="/claims" className="mb-4 inline-block text-sm text-slate-500 hover:text-slate-700">
        &larr; Back to claims
      </Link>

      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">{claim.claim_number}</h1>
          <p className="text-sm text-slate-500">Policy: {claim.policy_id}</p>
        </div>
        <StatusBadge status={claim.status} />
      </div>

      {saveError && <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{saveError}</div>}

      <div className="mb-6 rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="mb-4 text-sm font-semibold uppercase text-slate-500">Status</h2>
        {upcomingStatuses.length === 0 ? (
          <p className="text-sm text-slate-500">This claim has reached a final status.</p>
        ) : (
          <div className="flex gap-2">
            {upcomingStatuses.map((status) => (
              <button
                key={status}
                type="button"
                disabled={pendingStatus !== null}
                onClick={() => handleStatusChange(status)}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-100 disabled:opacity-50"
              >
                {pendingStatus === status ? "Updating..." : `Move to ${status.replace("_", " ")}`}
              </button>
            ))}
          </div>
        )}
      </div>

      <form onSubmit={handleSaveDetails} className="space-y-4 rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="text-sm font-semibold uppercase text-slate-500">Claim details</h2>

        <div className="text-sm text-slate-500">Type: {claim.claim_type}</div>

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
          <span className="mb-1 block text-slate-600">Description</span>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
          />
        </label>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={isSaving}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {isSaving ? "Saving..." : "Save changes"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function ClaimDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  return (
    <AuthGuard>
      <ClaimDetailInner claimId={id} />
    </AuthGuard>
  );
}
