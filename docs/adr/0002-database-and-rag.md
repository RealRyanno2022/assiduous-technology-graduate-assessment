# ADR 0002: Database choice and RAG retrieval

## Status
Accepted

## Context
The stack brief specifies PostgreSQL + a vector database for embeddings. The build
environment for this assignment has neither Docker nor a local Postgres instance
available, and no `ANTHROPIC_API_KEY`/embeddings key is configured.

## Decision
- Postgres + `pgvector` is the schema-of-record: `infra/docker-compose.yml` and
  `apps/api/alembic/` target it, and it's what `apps/api/Dockerfile` runs against in
  production/docker.
- `DATABASE_URL` defaults to a local SQLite file (`sqlite:///./senus.db`) when unset, so
  `make seed && make api` works with zero external setup. SQLAlchemy's dialect
  abstraction covers every table except `embeddings.embedding`, which is `Vector(1536)`
  under Postgres and a `JSON`-encoded float array under SQLite (see `models/embedding.py`).
- Retrieval for the `/insights` endpoint is **grounded, not semantic-searched**: with
  only one filing period of real data, a full vector-search RAG stack is unjustified
  complexity. Instead, `services/insights.py` retrieves the relevant `computed_metrics`
  and `financial_line_items` rows for the requested category/period directly (a
  structured-data retrieval, not a text-similarity one) and passes them to the LLM as
  grounding context. `embeddings` and the vector column exist and are wired up (narrative
  chunks from the PR notes are embedded when an embeddings key is present) so that true
  semantic RAG over unstructured narrative is a config change, not a rebuild, once more
  filings/documents exist.

## Consequences
- The demo runs anywhere with just Python + Node, no Docker required.
- Swapping to real Postgres is a one-line env var change; the schema and migrations are
  already Postgres-shaped.
- The "RAG" claim in the brief is honestly scoped: grounded generation today, with the
  vector-search path implemented and ready rather than faked.
