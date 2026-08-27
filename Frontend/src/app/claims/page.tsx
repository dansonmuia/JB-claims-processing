"use client";

import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";

import AuthGuard from "@/components/AuthGuard";
import StatusBadge from "@/components/StatusBadge";
import { ApiError, listClaims } from "@/lib/api";
import type { Claim } from "@/lib/types";

const PAGE_SIZE = 10;

function ClaimsListInner() {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [count, setCount] = useState(0);
  const [offset, setOffset] = useState(0);
  const [claimNumberFilter, setClaimNumberFilter] = useState("");
  const [policyIdFilter, setPolicyIdFilter] = useState("");
  const [appliedFilters, setAppliedFilters] = useState({ claim_number: "", policy_id: "" });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchClaims = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await listClaims({
        offset,
        limit: PAGE_SIZE,
        claim_number: appliedFilters.claim_number || undefined,
        policy_id: appliedFilters.policy_id || undefined,
      });
      setClaims(result.items);
      setCount(result.count);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load claims.");
    } finally {
      setIsLoading(false);
    }
  }, [offset, appliedFilters]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetching claims for the current page/filters
    fetchClaims();
  }, [fetchClaims]);

  const handleFilterSubmit = (event: FormEvent) => {
    event.preventDefault();
    setOffset(0);
    setAppliedFilters({ claim_number: claimNumberFilter.trim(), policy_id: policyIdFilter.trim() });
  };

  const handleClearFilters = () => {
    setClaimNumberFilter("");
    setPolicyIdFilter("");
    setOffset(0);
    setAppliedFilters({ claim_number: "", policy_id: "" });
  };

  const hasNextPage = offset + PAGE_SIZE < count;
  const hasPrevPage = offset > 0;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Claims</h1>
        <Link
          href="/claims/new"
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          New Claim
        </Link>
      </div>

      <form onSubmit={handleFilterSubmit} className="mb-6 flex flex-wrap items-end gap-3">
        <label className="text-sm">
          <span className="mb-1 block text-slate-600">Claim number</span>
          <input
            value={claimNumberFilter}
            onChange={(e) => setClaimNumberFilter(e.target.value)}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-slate-500 focus:outline-none"
            placeholder="CLM-0001"
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-slate-600">Policy ID</span>
          <input
            value={policyIdFilter}
            onChange={(e) => setPolicyIdFilter(e.target.value)}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-slate-500 focus:outline-none"
            placeholder="UUID"
          />
        </label>
        <button
          type="submit"
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-100"
        >
          Filter
        </button>
        <button
          type="button"
          onClick={handleClearFilters}
          className="rounded-md px-3 py-1.5 text-sm text-slate-500 hover:text-slate-700"
        >
          Clear
        </button>
      </form>

      {error && <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Claim #</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Amount</th>
              <th className="px-4 py-3">Incident Date</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                  Loading...
                </td>
              </tr>
            )}
            {!isLoading && claims.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                  No claims found.
                </td>
              </tr>
            )}
            {!isLoading &&
              claims.map((claim) => (
                <tr key={claim.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
                  <td className="px-4 py-3">
                    <Link href={`/claims/${claim.id}`} className="font-medium text-slate-900 hover:underline">
                      {claim.claim_number}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{claim.claim_type}</td>
                  <td className="px-4 py-3 text-slate-600">{Number(claim.claim_amount).toLocaleString()}</td>
                  <td className="px-4 py-3 text-slate-600">{claim.incident_date}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={claim.status} />
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center justify-between text-sm text-slate-600">
        <span>
          Showing {claims.length === 0 ? 0 : offset + 1}-{offset + claims.length} of {count}
        </span>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={!hasPrevPage}
            onClick={() => setOffset((prev) => Math.max(prev - PAGE_SIZE, 0))}
            className="rounded-md border border-slate-300 px-3 py-1.5 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Previous
          </button>
          <button
            type="button"
            disabled={!hasNextPage}
            onClick={() => setOffset((prev) => prev + PAGE_SIZE)}
            className="rounded-md border border-slate-300 px-3 py-1.5 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

export default function ClaimsPage() {
  return (
    <AuthGuard>
      <ClaimsListInner />
    </AuthGuard>
  );
}
