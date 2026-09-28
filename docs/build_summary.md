# Senus PLC Board Report — Write-up

Assiduous Technology Graduate Assessment. Repo: [assiduous-technology-graduate-assessment](https://github.com/RealRyanno2022/assiduous-technology-graduate-assessment)

## What was built

An AI-native platform that extracts Senus PLC's HY2026 half-year results into a
database and serves them as an interactive Board Report, addressing all four readers
the brief names — Management, the Board, Equity Investors, Credit Providers — with a
role-scoped view **enforced server-side** (a disallowed category 403s, not just a
hidden nav link), plus an AI-drafted Directors' Report narrative meant to save real
time on public correspondence. FastAPI + SQLAlchemy + Postgres/pgvector backend,
Next.js/TypeScript frontend, Claude for extraction and commentary, Docker Compose +
GitHub Actions CI. **30/30 backend tests passing.**

## Key decisions

- **LLM extraction over table-parsing** ([ADR 0001](adr/0001-extraction-strategy.md)):
  bookings and pipeline value only exist in the filing's prose, not its statement
  tables. Claude extracts to a strict JSON schema; a deterministic regex parser is the
  offline fallback when no API key is set — both paths hit the same reconciliation
  validator before being trusted, and a failing row is flagged `failed_validation`
  rather than silently accepted.
- **Postgres+pgvector as schema-of-record, SQLite for local dev**
  ([ADR 0002](adr/0002-database-and-rag.md)): `/insights` uses grounded retrieval
  (the relevant `computed_metrics`/`financial_line_items` rows, not vector search) —
  honestly scoped, since only one filing period of data exists today.
- **Access is nested, not four separate views**: Management sees everything; Board
  sees everything except two operational sales-tracking figures; Equity Investors get
  full depth on Growth/Returns with balance-sheet detail trimmed to headline; Credit
  Providers get full depth on Cash/Solvency with Returns hidden entirely (ROCE isn't a
  lender's concern).

## Assumptions & validation

Only the HY2026 PR was available at build time, so `filing_periods` also holds a
lightweight FY2025 context period from the PR's own reference materials — flagged
on-page, not hidden. DSCR uses EBITDA/interest as a proxy (no repayment schedule
disclosed); ROCE and DSCR are both explicitly flagged as not yet meaningful for a
pre-scale business. `test_reconciliation.py` includes a deliberately corrupted input to
prove the validator catches mismatches; metrics tests assert against the filing's own
printed figures. **Two real bugs were caught this way** during development (a
balance-sheet sign-convention error, a reconciliation rule with a flipped sign) and are
now regression-tested. Chart colors were run through a CVD (colorblindness) validator
rather than chosen by eye — the original green/red KPI coloring failed outright and was
replaced with a validated pair plus a mandatory arrow icon.

## AI-assisted development

Built end to end with **Claude Code** (Claude Sonnet 5) — architecture, backend,
frontend, the role-based access system, CI/CD, this write-up. Every change was
verified, not just generated: tests run after each backend change, the app driven live
in a browser after each frontend change (all four role logins checked individually),
colors validated automatically rather than eyeballed.

## Status

Backend fully tested (extraction, metrics, reconciliation, role access, Directors'
Report generator); frontend verified live across all four roles; CI runs tests + a
Next.js build + a full `docker compose up` smoke test on every push. Frontend is live
on Vercel; API + Postgres are built for Render (`render.yaml`, `Dockerfile` committed)
but weren't live at submission time — the demo runs against the local API.
