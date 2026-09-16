"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, login, type Role } from "@/lib/api";

// Each role lands on the page matching their primary concern rather than a
// one-size-fits-all overview - mirrors the "full" categories per role in
// app/services/role_access.py (see Nav.tsx for the same mapping applied to the sidebar)
const ROLE_LANDING: Record<Role, string> = {
  management: "/dashboard",
  board: "/dashboard/insights",
  equity_investor: "/dashboard/returns",
  credit_provider: "/dashboard/cash-liquidity",
};

const DEMO_ACCOUNTS = [
  { email: "management@senus.com", label: "Management", hint: "Full detail, every category" },
  { email: "board@senus.com", label: "Board", hint: "Full on cash, solvency & returns - growth & profitability headline-only" },
  { email: "investor@senus.com", label: "Equity Investor", hint: "Growth & returns in depth, everything else headline-only" },
  { email: "lender@senus.com", label: "Credit Provider", hint: "Cash & solvency in depth, returns hidden" },
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("management@senus.com");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const role = await login(email, password);
      router.replace(ROLE_LANDING[role]);
    } catch (err) {
      // ApiError means the server actually responded (a real auth failure);
      // anything else (network/CORS/blocked) is a connectivity problem, not a
      // bad password - conflating the two makes real outages look like typos.
      setError(err instanceof ApiError ? err.message : "Could not reach the server - check your connection");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 16,
      }}
    >
      <form onSubmit={onSubmit} className="card" style={{ width: 400, display: "flex", flexDirection: "column", gap: 14 }}>
        <div>
          <div style={{ fontSize: 12, letterSpacing: "0.06em", color: "var(--accent)", fontWeight: 600, textTransform: "uppercase" }}>
            Senus PLC
          </div>
          <h1 style={{ fontSize: 22, margin: "6px 0 0" }}>Board Report</h1>
          <p className="muted" style={{ fontSize: 13.5, margin: "4px 0 0" }}>Sign in to view HY2026 performance</p>
        </div>

        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 13.5 }}>
          Email
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            required
            style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid var(--border)", background: "var(--bg)", color: "var(--ink)" }}
          />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 13.5 }}>
          Password
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            required
            style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid var(--border)", background: "var(--bg)", color: "var(--ink)" }}
          />
        </label>

        {error && (
          <div style={{ background: "var(--danger-soft)", color: "var(--danger)", padding: "8px 10px", borderRadius: 8, fontSize: 13 }}>
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            background: "var(--accent)",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            padding: "10px 12px",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>

        <div style={{ borderTop: "1px solid var(--border)", paddingTop: 12, display: "flex", flexDirection: "column", gap: 6 }}>
          <p className="faint" style={{ fontSize: 11, margin: "0 0 2px", textTransform: "uppercase", letterSpacing: "0.04em" }}>
            Demo accounts &middot; password senus2030 for all
          </p>
          {DEMO_ACCOUNTS.map((acct) => (
            <button
              key={acct.email}
              type="button"
              onClick={() => setEmail(acct.email)}
              style={{
                textAlign: "left",
                background: email === acct.email ? "var(--accent-soft)" : "transparent",
                border: "1px solid var(--border)",
                borderRadius: 8,
                padding: "7px 10px",
                cursor: "pointer",
                color: "var(--ink)",
              }}
            >
              <div style={{ fontSize: 12.5, fontWeight: 600 }}>{acct.label}</div>
              <div className="faint" style={{ fontSize: 11 }}>{acct.hint}</div>
            </button>
          ))}
        </div>
      </form>
    </main>
  );
}
