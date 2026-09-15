# Senus PLC — Board Report

An AI-native platform that extracts Senus PLC's reported financials into a database
and serves them as an interactive Board Report — built for the Assiduous Technology
Graduate assessment. The brief names four Board Report readers with different
concerns — **Management, the Board, Equity Investors, Credit Providers** — so each
gets a role-scoped view, enforced server-side, plus an AI-drafted **Directors' Report**
narrative meant to save real time on public correspondence, not just another chart.

## Demo accounts

Password `senus2030` for all.

| Email | Role | View |
|---|---|---|
| `management@senus.com` | Management | Full detail, every category |
| `board@senus.com` | Board | Everything except two sales-ops figures |
| `investor@senus.com` | Equity Investor | Growth & Returns in depth; balance sheet headline-only |
| `lender@senus.com` | Credit Provider | Cash & Solvency in depth; Returns hidden |

## Architecture

```
apps/api/    FastAPI backend - extraction, metrics, AI insights, auth
apps/web/    Next.js (App Router, TypeScript) frontend
infra/       docker-compose.yml (Postgres + API + web)
data/raw/    The source filing the extraction pipeline runs against
docs/        ADRs and the ERD
```

Decisions are written up as ADRs rather than restated here:
[extraction strategy](docs/adr/0001-extraction-strategy.md) ·
[database & RAG](docs/adr/0002-database-and-rag.md) · [ERD](docs/erd.md)

**Stack:** FastAPI, SQLAlchemy, Alembic, Postgres+pgvector (SQLite for local dev),
Next.js 14 + TypeScript, Recharts, Claude (Anthropic API), Docker Compose, GitHub
Actions CI.

## AI-native, concretely

`extraction.py` sends the HY2026 filing to Claude with a strict JSON schema, falling
back to a deterministic parser when no `ANTHROPIC_API_KEY` is set - both paths produce
the same output. Bookings, pipeline value and the Senus 2030 targets are pulled from
the filing's **prose**, not its tables - the case a table parser can't reach. Every
figure is reconciled against its components (`schema.py`) before being trusted; a
failing row is flagged `failed_validation`, not silently accepted. `directors_report.py`
drafts the actual narrative document from validated data. `insights.py` grounds
per-category commentary and free-form Q&A in the same data. Every AI output has a
non-AI fallback, so the app runs with zero external dependencies - the LLM path is the
intended one, used whenever a key is configured.

## Assumptions & validation

Only the HY2026 PR was available at build time (not the FY25 annual report), so
`filing_periods` also holds a lightweight FY2025 context period from the PR's own
reference materials. MoM trend and channel splits aren't disclosed, so only HY-vs-HY
is shown (flagged on-page). DSCR uses EBITDA/interest as a proxy since no principal
repayment schedule is disclosed. ROCE and DSCR are both explicitly flagged as not yet
meaningful for a pre-scale business rather than dressed up.

Validation is a real check, not a claim: `test_reconciliation.py` includes a
deliberately corrupted input to prove the validator catches mismatches; metrics tests
assert against the filing's own printed figures. Two real bugs were caught this way
during development (a balance-sheet sign convention error, a reconciliation rule with
a flipped sign) and are now regression-tested. Chart colors were run through a CVD
(colorblindness) validator rather than chosen by eye - the original green/red KPI
coloring failed outright and was replaced. 30 backend tests pass; CI runs them plus a
Next.js build plus a full `docker compose up` smoke test on every push.

## AI-assisted development workflow

Built end to end with **Claude Code** (Claude Sonnet 5) - architecture, backend,
frontend, the role-based access system, CI/CD, this README. Every change was verified,
not just generated: tests run after each backend change, the app driven live in a
browser after each frontend change (each of the four role logins checked individually),
colors validated automatically rather than eyeballed. Bugs the model introduced were
caught by running the code against the filing's real numbers, not assumed correct.

## Getting started

```bash
# API (SQLite, no Docker needed)
cd apps/api && python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/seed.py && .venv/bin/uvicorn app.main:app --reload --port 8000

# Web
cd apps/web && npm install && npm run dev   # set NEXT_PUBLIC_API_URL=http://localhost:8000

# Or: everything via Docker
cd infra && docker compose up --build

# Tests
cd apps/api && pytest -q
```

## Deployment

Frontend is on Vercel. API + Postgres are built for Render (`render.yaml`,
`apps/api/Dockerfile`) but weren't live at submission time - the demo runs against the
local API. Everything needed to finish that deployment is already in the repo.
