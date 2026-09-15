"use client";

import { useEffect, useState } from "react";
import type { CategoryResponse } from "@/lib/api";
import { ApiError } from "@/lib/api";
import KpiTile from "@/components/KpiTile";
import ComparisonChart from "@/components/ComparisonChart";
import { formatLineItemValue } from "@/lib/format";

export default function CategoryView({
  title,
  description,
  fetcher,
  dataGapNote,
}: {
  title: string;
  description: string;
  fetcher: () => Promise<CategoryResponse>;
  dataGapNote?: string;
}) {
  const [data, setData] = useState<CategoryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetcher()
      .then(setData)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Failed to load"));
  }, [fetcher]);

  if (error) return <div className="card" style={{ color: "var(--danger)" }}>{error}</div>;
  if (!data) return <div className="muted">Loading...</div>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div>
        <h1 style={{ fontSize: 22, margin: 0 }}>{title}</h1>
        <p className="muted" style={{ fontSize: 13.5, margin: "4px 0 0" }}>{description}</p>
        <p className="faint" style={{ fontSize: 12, margin: "4px 0 0" }}>
          {data.period_label} &middot; {data.period_start} to {data.period_end} &middot; {data.is_audited ? "Audited" : "Unaudited"}
        </p>
      </div>

      {dataGapNote && (
        <div
          className="faint"
          style={{
            fontSize: 12.5,
            background: "var(--surface)",
            border: "1px dashed var(--border)",
            borderRadius: 8,
            padding: "8px 12px",
          }}
        >
          {dataGapNote}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12 }}>
        {data.metrics.map((m) => (
          <KpiTile key={m.metric_key} metricKey={m.metric_key} value={m.metric_value} unit={m.unit} />
        ))}
      </div>

      <ComparisonChart lineItems={data.line_items} periodLabel={data.period_label} />

      <div className="card" style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ textAlign: "left", color: "var(--ink-faint)", fontSize: 11.5 }}>
              <th style={{ padding: "6px 8px" }}>Statement</th>
              <th style={{ padding: "6px 8px" }}>Line item</th>
              <th style={{ padding: "6px 8px", textAlign: "right" }}>{data.period_label}</th>
              <th style={{ padding: "6px 8px", textAlign: "right" }}>Prior period</th>
              <th style={{ padding: "6px 8px" }}>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {data.line_items.map((li) => (
              <tr key={li.line_item} style={{ borderTop: "1px solid var(--border)" }}>
                <td style={{ padding: "6px 8px" }} className="faint">{li.statement}</td>
                <td style={{ padding: "6px 8px" }}>{li.line_item.replace(/_/g, " ")}</td>
                <td style={{ padding: "6px 8px", textAlign: "right", fontFamily: "monospace" }}>{formatLineItemValue(li.line_item, li.value_eur)}</td>
                <td style={{ padding: "6px 8px", textAlign: "right", fontFamily: "monospace" }} className="muted">
                  {li.comparative_value_eur !== null ? formatLineItemValue(li.line_item, li.comparative_value_eur) : "—"}
                </td>
                <td style={{ padding: "6px 8px" }}>
                  <span
                    style={{
                      fontSize: 11,
                      padding: "2px 7px",
                      borderRadius: 99,
                      background: li.extraction_confidence === "extracted" ? "var(--accent-soft)" : "var(--danger-soft)",
                      color: li.extraction_confidence === "extracted" ? "var(--accent)" : "var(--danger)",
                    }}
                  >
                    {li.extraction_confidence}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
