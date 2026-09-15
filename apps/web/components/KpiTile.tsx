import { formatMetric, metricLabel, metricTone } from "@/lib/format";

export default function KpiTile({ metricKey, value, unit }: { metricKey: string; value: number; unit: string }) {
  const tone = metricTone(metricKey, value);
  const color = tone === "good" ? "var(--status-good)" : tone === "bad" ? "var(--status-critical)" : "var(--ink)";
  // color never carries meaning alone - the arrow is the non-color cue for sign
  const arrow = tone === "good" ? "▲" : tone === "bad" ? "▼" : null;

  return (
    <div className="card">
      <div className="faint" style={{ fontSize: 11.5, marginBottom: 6 }}>
        {metricLabel(metricKey)}
      </div>
      <div style={{ fontSize: 20, fontWeight: 700, color, display: "flex", alignItems: "baseline", gap: 5 }}>
        {arrow && <span style={{ fontSize: 12 }} aria-hidden="true">{arrow}</span>}
        <span>{formatMetric(value, unit)}</span>
      </div>
    </div>
  );
}
