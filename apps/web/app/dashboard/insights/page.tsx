"use client";

import { useEffect, useState } from "react";
import { ApiError, askInsights, getInsights, type InsightOut } from "@/lib/api";

export default function InsightsPage() {
  const [insights, setInsights] = useState<InsightOut[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    getInsights()
      .then(setInsights)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Failed to load"));
  }, []);

  async function onAsk(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;
    setAsking(true);
    setAnswer(null);
    try {
      const res = await askInsights(question);
      setAnswer(res.answer);
    } catch (e) {
      setAnswer(e instanceof ApiError ? e.message : "Failed to get an answer");
    } finally {
      setAsking(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div>
        <h1 style={{ fontSize: 22, margin: 0 }}>AI Insights</h1>
        <p className="muted" style={{ fontSize: 13.5, margin: "4px 0 0" }}>
          Commentary grounded in the extracted HY2026 figures, plus ad-hoc Q&amp;A over the same data.
        </p>
      </div>

      {error && <div className="card" style={{ color: "var(--danger)" }}>{error}</div>}
      {!insights && !error && <div className="muted">Loading...</div>}

      {insights && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 14 }}>
          {insights.map((insight) => (
            <div key={insight.category} className="card">
              <div className="faint" style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 6 }}>
                {insight.title}
              </div>
              <p style={{ fontSize: 13.5, lineHeight: 1.55, margin: 0 }}>{insight.body}</p>
              <div className="faint" style={{ fontSize: 10.5, marginTop: 10 }}>{insight.model}</div>
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <div style={{ fontSize: 13.5, fontWeight: 600, marginBottom: 10 }}>Ask a question about this report</div>
        <form onSubmit={onAsk} style={{ display: "flex", gap: 8 }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. Why is cash healthy if operating cash flow is negative?"
            style={{
              flex: 1,
              padding: "8px 10px",
              borderRadius: 8,
              border: "1px solid var(--border)",
              background: "var(--bg)",
              color: "var(--ink)",
              fontSize: 13.5,
            }}
          />
          <button
            type="submit"
            disabled={asking}
            style={{
              background: "var(--accent)",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              padding: "8px 16px",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {asking ? "Thinking..." : "Ask"}
          </button>
        </form>
        {answer && (
          <p style={{ fontSize: 13.5, lineHeight: 1.55, marginTop: 14, marginBottom: 0 }}>{answer}</p>
        )}
      </div>
    </div>
  );
}
