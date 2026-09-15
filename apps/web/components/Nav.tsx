"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken, getFullName, getRole, type Role } from "@/lib/api";

const ITEMS: { href: string; label: string; category?: string }[] = [
  { href: "/dashboard", label: "Directors' Report" },
  { href: "/dashboard/growth", label: "Growth & Revenue", category: "growth" },
  { href: "/dashboard/profitability", label: "Profitability", category: "profitability" },
  { href: "/dashboard/cash-liquidity", label: "Cash & Liquidity", category: "cash_liquidity" },
  { href: "/dashboard/solvency", label: "Solvency & Leverage", category: "solvency" },
  { href: "/dashboard/returns", label: "Returns", category: "returns" },
  { href: "/dashboard/insights", label: "AI Insights" },
];

// Mirrors the "hidden" entries in app/services/role_access.py - the backend is the
// real enforcement (a hidden category still 403s if requested directly); this just
// keeps the nav from linking to a page that role can't open
const ROLE_LABELS: Record<Role, string> = {
  management: "Management",
  board: "Board",
  equity_investor: "Equity Investor",
  credit_provider: "Credit Provider",
};
const HIDDEN_CATEGORIES: Partial<Record<Role, string[]>> = {
  credit_provider: ["returns"],
};

export default function Nav() {
  const pathname = usePathname();
  const router = useRouter();
  const [role, setRole] = useState<Role | null>(null);
  const [fullName, setFullName] = useState<string | null>(null);

  useEffect(() => {
    setRole(getRole());
    setFullName(getFullName());
  }, []);

  const hidden = new Set(role ? HIDDEN_CATEGORIES[role] ?? [] : []);
  const items = ITEMS.filter((item) => !item.category || !hidden.has(item.category));

  return (
    <nav
      style={{
        width: 220,
        flexShrink: 0,
        borderRight: "1px solid var(--border)",
        padding: "20px 14px",
        display: "flex",
        flexDirection: "column",
        gap: 4,
        minHeight: "100vh",
      }}
    >
      <div style={{ padding: "0 8px 18px" }}>
        <div style={{ fontSize: 11.5, letterSpacing: "0.06em", color: "var(--accent)", fontWeight: 700, textTransform: "uppercase" }}>
          Senus PLC
        </div>
        <div style={{ fontSize: 15, fontWeight: 600, fontFamily: "var(--font-serif)" }}>Board Report</div>
        {role && (
          <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 3 }}>
            <span className="role-badge" style={{ width: "fit-content" }}>{ROLE_LABELS[role]}</span>
            {fullName && <span className="faint" style={{ fontSize: 11 }}>{fullName}</span>}
          </div>
        )}
      </div>
      {items.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            style={{
              padding: "9px 10px",
              borderRadius: 8,
              fontSize: 13.5,
              textDecoration: "none",
              background: active ? "var(--accent-soft)" : "transparent",
              color: active ? "var(--accent)" : "var(--ink-soft)",
              fontWeight: active ? 600 : 500,
            }}
          >
            {item.label}
          </Link>
        );
      })}
      <div style={{ flex: 1 }} />
      <button
        onClick={() => {
          clearToken();
          delete document.body.dataset.role;
          router.replace("/login");
        }}
        style={{
          textAlign: "left",
          padding: "9px 10px",
          borderRadius: 8,
          fontSize: 13.5,
          border: "none",
          background: "transparent",
          color: "var(--ink-faint)",
          cursor: "pointer",
        }}
      >
        Sign out
      </button>
    </nav>
  );
}
