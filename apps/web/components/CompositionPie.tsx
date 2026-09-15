"use client";

import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

// Fixed order, validated categorical slots 1-3 (the only ones that clear the harder
// all-pairs CVD gate together - see dataviz skill palette.md) - never cycled, never
// reordered per-chart, so a slice's color always means the same series identity
const SLICE_COLORS = ["var(--series-1)", "var(--series-2)", "var(--series-3)"];
const RADIAN = Math.PI / 180;

export type CompositionSlice = { label: string; value: number };

type LabelArgs = { cx: number; cy: number; midAngle: number; innerRadius: number; outerRadius: number; percent: number };

// Labels sit inside the colored slice - the one case marks-and-anatomy.md allows for
// text on a data fill - so they carry a dark stroke behind white fill for contrast
// against any of the three slice hues, rather than branching per-color luminance
function renderSliceLabel({ cx, cy, midAngle, innerRadius, outerRadius, percent }: LabelArgs) {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.62;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  return (
    <text x={x} y={y} textAnchor="middle" dominantBaseline="central" fontSize={12} fontWeight={700} fill="#fff" stroke="rgba(0,0,0,0.4)" strokeWidth={3} paintOrder="stroke">
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
}

export default function CompositionPie({ title, slices }: { title: string; slices: CompositionSlice[] }) {
  const total = slices.reduce((sum, s) => sum + s.value, 0);
  if (total <= 0) return null;

  return (
    <div className="card" style={{ height: 280 }}>
      <div className="faint" style={{ fontSize: 11.5, marginBottom: 4 }}>
        {title}
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={slices}
            dataKey="value"
            nameKey="label"
            cx="50%"
            cy="50%"
            innerRadius={0}
            outerRadius={85}
            paddingAngle={2}
            // every slice is labeled directly (a 2-3 slice pie is exactly the "selective
            // labeling" case, not the "flood every point" anti-pattern) since the aqua
            // slot sits below the 3:1 contrast floor and needs this relief channel
            label={renderSliceLabel}
            labelLine={false}
            animationDuration={700}
            animationEasing="ease-out"
          >
            {slices.map((s, i) => (
              <Cell key={s.label} fill={SLICE_COLORS[i % SLICE_COLORS.length]} stroke="var(--surface)" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number, label: string) => [
              new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(value),
              label,
            ]}
            contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
