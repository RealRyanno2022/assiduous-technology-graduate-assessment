import { formatMetric, metricLabel } from "@/lib/format";

export default function KpiTile({
  metricKey,
  value,
  unit,
  tone,
}: {
  metricKey: string;
  value: number;
  unit: string;
  tone?: "good" | "bad" | "neutral";
}) {
  const resolvedTone = tone ?? (unit === "pct" || unit === "eur" ? (value >= 0 ? "good" : "bad") : "neutral");
  const color = resolvedTone === "good" ? "var(--accent)" : resolvedTone === "bad" ? "var(--danger)" : "var(--ink)";

  return (
    <div className="card">
      <div className="faint" style={{ fontSize: 11.5, marginBottom: 6 }}>
        {metricLabel(metricKey)}
      </div>
      <div style={{ fontSize: 20, fontWeight: 700, color }}>{formatMetric(value, unit)}</div>
    </div>
  );
}
