FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# build context is the repo root (see infra/docker-compose.yml) so this can also copy data/
COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api/ .
COPY data/ /app/data/

ENV SOURCE_PDF_PATH=/app/data/raw/senus_hy2026_results_pr.pdf

EXPOSE 8000

# migrate, extract+seed from the source PDF, then serve - idempotent, safe to re-run on restart
CMD ["sh", "-c", "alembic upgrade head && python scripts/seed.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
