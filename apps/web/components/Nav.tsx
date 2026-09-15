"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken } from "@/lib/api";

const ITEMS = [
  { href: "/dashboard", label: "Directors' Report" },
  { href: "/dashboard/growth", label: "Growth & Revenue" },
  { href: "/dashboard/profitability", label: "Profitability" },
  { href: "/dashboard/cash-liquidity", label: "Cash & Liquidity" },
  { href: "/dashboard/solvency", label: "Solvency & Leverage" },
  { href: "/dashboard/returns", label: "Returns" },
  { href: "/dashboard/insights", label: "AI Insights" },
];

export default function Nav() {
  const pathname = usePathname();
  const router = useRouter();

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
        <div style={{ fontSize: 15, fontWeight: 600 }}>Board Report</div>
      </div>
      {ITEMS.map((item) => {
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
