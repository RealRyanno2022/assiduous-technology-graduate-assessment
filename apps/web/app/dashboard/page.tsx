"use client";

import { useEffect, useState } from "react";
import { ApiError, getDirectorsReport, type DirectorsReportResponse } from "@/lib/api";

export default function DirectorsReportPage() {
  const [data, setData] = useState<DirectorsReportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [regenerating, setRegenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  function load(refresh = false) {
    if (refresh) setRegenerating(true);
    getDirectorsReport(refresh)
      .then((res) => {
        setData(res);
        setError(null);
      })
      .catch((e) => setError(e instanceof ApiError ? e.message : "Failed to load"))
      .finally(() => setRegenerating(false));
  }

  useEffect(() => load(), []);

  async function onCopy() {
    if (!data) return;
    const text = data.sections.map((s) => `${s.heading}\n\n${s.body}`).join("\n\n");
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard permission denied - nothing to do, the text is still selectable on screen
    }
  }

  if (error) return <div className="card" style={{ color: "var(--danger)" }}>{error}</div>;
  if (!data) return <div className="muted">Drafting the report...</div>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20, maxWidth: 760 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 22, margin: 0 }}>Directors&rsquo; Report</h1>
          <p className="muted" style={{ fontSize: 13.5, margin: "4px 0 0" }}>
            An AI-drafted narrative for {data.period_label}, ready to review and adapt for public correspondence - not
            a document to file as-is, but a first draft that should save far more time than starting from a blank page.
          </p>
        </div>
        <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
          <button
            onClick={onCopy}
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              padding: "8px 14px",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
              color: "var(--ink)",
            }}
          >
            {copied ? "Copied" : "Copy text"}
          </button>
          <button
            onClick={() => load(true)}
            disabled={regenerating}
            style={{
              background: "var(--accent)",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              padding: "8px 14px",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {regenerating ? "Redrafting..." : "Regenerate"}
          </button>
        </div>
      </div>

      <div className="card" style={{ padding: "28px 32px", lineHeight: 1.65 }}>
        {data.sections.map((section) => (
          <div key={section.heading} style={{ marginBottom: 22 }}>
            <h2 style={{ fontSize: 15, margin: "0 0 8px", color: "var(--accent)" }}>{section.heading}</h2>
            <p style={{ fontSize: 14.5, margin: 0 }}>{section.body}</p>
          </div>
        ))}
      </div>

      <p className="faint" style={{ fontSize: 11.5 }}>
        Drafted by {data.model} from the extracted, reconciliation-validated HY2026 figures - see the metric pages for
        the source line items behind every number cited here.
      </p>
    </div>
  );
}
