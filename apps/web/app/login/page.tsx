"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("ceo@senus.com");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
      router.replace("/dashboard");
    } catch {
      setError("Incorrect email or password");
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
      <form onSubmit={onSubmit} className="card" style={{ width: 360, display: "flex", flexDirection: "column", gap: 14 }}>
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

        <p className="faint" style={{ fontSize: 11.5, margin: 0 }}>
          Demo credentials: ceo@senus.com / senus2030
        </p>
      </form>
    </main>
  );
}
