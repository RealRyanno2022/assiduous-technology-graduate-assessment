# ADR 0001: Financial data extraction strategy

## Status
Accepted

## Context
The only source document available at build time is the HY2026 Half Year Results
announcement (`data/raw/senus_hy2026_results_pr.pdf`) — a 9-page PR with narrative
(highlights, Chairman's statement, Senus 2030 strategy) plus a full Consolidated P&L,
Balance Sheet and Cash Flow Statement for HY2026 vs HY25.

Two extraction strategies were considered:

1. **Table-parsing (regex/coordinates)** — fast, deterministic, but brittle across
   filing formats and blind to narrative facts (pipeline value, EBITDA-positive target
   year) that the AI insights layer needs to ground commentary in.
2. **LLM structured extraction** — an LLM reads the filing text and returns typed,
   schema-validated JSON. Generalises across formats and reaches narrative facts a
   table parser cannot.

## Decision
Use LLM structured extraction (Claude, via the Anthropic API) as the primary pipeline,
with a deterministic offline fallback for local dev/CI when no API key is configured.

- `extract_with_llm` sends the PDF's extracted text to Claude with a strict JSON schema
  (statement / line_item / value / comparative_value / unit).
- `extract_offline` is a rule-based parser over the same text, used when
  `ANTHROPIC_API_KEY` is unset, so `make seed`/CI work with zero external dependencies.
- Both paths return the same `ExtractedLineItem` model and go through the same
  reconciliation validator before being written to `financial_line_items`:
  - `turnover - cost_of_sales == gross_profit` (±€1 rounding)
  - `gross_profit - administrative_expenses + other_operating_income == group_operating_loss`
  - `group_operating_loss - interest_payable == loss_before_taxation`
  - `total_assets_less_current_liabilities - non_current_liabilities == net_assets`
  - `net_assets == called_up_share_capital + share_premium + retained_earnings`

  A row that fails reconciliation is stored with `extraction_confidence = 'failed_validation'`
  and excluded from `computed_metrics` rather than silently trusted.

## Consequences
- The extraction step is a real, testable AI integration rather than a static seed file.
- Every `financial_line_item` keeps a `raw_snippet` and `source_document_id` so any
  dashboard number traces back to the source text it came from.
- Only one filing exists today, so `filing_periods` holds HY2026 (fully extracted) and
  FY2025 (revenue + customer count only, from the same PR's reference materials) —
  documented as an explicit assumption rather than hidden.
