"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken, getFullName, getRole, type Role } from "@/lib/api";

const CATEGORY_ITEMS: { href: string; label: string; category: string }[] = [
  { href: "/dashboard/growth", label: "Growth & Revenue", category: "growth" },
  { href: "/dashboard/profitability", label: "Profitability", category: "profitability" },
  { href: "/dashboard/cash-liquidity", label: "Cash & Liquidity", category: "cash_liquidity" },
  { href: "/dashboard/solvency", label: "Solvency & Leverage", category: "solvency" },
  { href: "/dashboard/returns", label: "Returns", category: "returns" },
];

const ROLE_LABELS: Record<Role, string> = {
  management: "Management",
  board: "Board",
  equity_investor: "Equity Investor",
  credit_provider: "Credit Provider",
};

// Exact mirror of ROLE_ACCESS in app/services/role_access.py - the backend is the
// real enforcement (a disallowed category still 403s if requested directly); this
// drives which categories lead each role's sidebar vs sit in a lower-priority
// "also available" section, so the nav reflects what's actually relevant per role
// rather than one uniform list for everyone.
type AccessLevel = "full" | "summary" | "hidden";
const ROLE_ACCESS: Record<Role, Record<string, AccessLevel>> = {
  management: { growth: "full", profitability: "full", cash_liquidity: "full", solvency: "full", returns: "full" },
  board: { growth: "summary", profitability: "summary", cash_liquidity: "full", solvency: "full", returns: "full" },
  equity_investor: { growth: "full", profitability: "summary", cash_liquidity: "summary", solvency: "summary", returns: "full" },
  credit_provider: { growth: "summary", profitability: "summary", cash_liquidity: "full", solvency: "full", returns: "hidden" },
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

  const access = role ? ROLE_ACCESS[role] : {};
  const primaryCategories = CATEGORY_ITEMS.filter((item) => access[item.category] === "full");
  const secondaryCategories = CATEGORY_ITEMS.filter((item) => access[item.category] === "summary");

  function renderLink(item: { href: string; label: string }, faint = false) {
    const active = pathname === item.href;
    return (
      <Link
        key={item.href}
        href={item.href}
        style={{
          padding: "9px 10px",
          borderRadius: 8,
          fontSize: faint ? 12.5 : 13.5,
          textDecoration: "none",
          background: active ? "var(--accent-soft)" : "transparent",
          color: active ? "var(--accent)" : faint ? "var(--ink-faint)" : "var(--ink-soft)",
          fontWeight: active ? 600 : 500,
        }}
      >
        {item.label}
      </Link>
    );
  }

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
      {renderLink({ href: "/dashboard", label: "Directors' Report" })}
      {primaryCategories.map((item) => renderLink(item))}
      {renderLink({ href: "/dashboard/insights", label: "AI Insights" })}

      {secondaryCategories.length > 0 && (
        <>
          <div
            className="faint"
            style={{ padding: "14px 10px 4px", fontSize: 10.5, letterSpacing: "0.05em", textTransform: "uppercase" }}
          >
            Also available (summary)
          </div>
          {secondaryCategories.map((item) => renderLink(item, true))}
        </>
      )}

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
