"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth-context";

export default function Navbar() {
  const { admin, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  if (!isAuthenticated) return null;

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link href="/claims" className="text-lg font-semibold text-slate-900">
          JB Claims Portal
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link href="/claims" className="text-slate-600 hover:text-slate-900">
            Claims
          </Link>
          <Link href="/claims/new" className="text-slate-600 hover:text-slate-900">
            New Claim
          </Link>
          {admin && (
            <span className="text-slate-400">
              {admin.name} &middot; {admin.role}
            </span>
          )}
          <button
            type="button"
            onClick={handleLogout}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-slate-700 hover:bg-slate-100"
          >
            Log out
          </button>
        </nav>
      </div>
    </header>
  );
}
