"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { LineItemOut } from "@/lib/api";
import { metricLabel } from "@/lib/format";

export default function ComparisonChart({ lineItems, periodLabel }: { lineItems: LineItemOut[]; periodLabel: string }) {
  const data = lineItems
    .filter((li) => li.comparative_value_eur !== null)
    .map((li) => ({
      name: metricLabel(li.line_item),
      [periodLabel]: li.value_eur,
      Prior: li.comparative_value_eur,
    }));

  if (data.length === 0) return null;

  return (
    <div className="card" style={{ height: 320 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="name" angle={-30} textAnchor="end" interval={0} height={70} tick={{ fontSize: 11 }} stroke="var(--ink-faint)" />
          <YAxis tick={{ fontSize: 11 }} stroke="var(--ink-faint)" />
          <Tooltip
            formatter={(value: number) => new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(value)}
            contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="Prior" fill="var(--border)" radius={[4, 4, 0, 0]} />
          <Bar dataKey={periodLabel} fill="var(--accent)" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
