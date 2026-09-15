.PHONY: api-install api-test api-seed api-dev web-install web-dev up down

api-install:
	cd apps/api && python -m venv .venv && .venv/bin/pip install -r requirements.txt

api-test:
	cd apps/api && .venv/bin/pytest -q

api-seed:
	cd apps/api && .venv/bin/python scripts/seed.py

api-dev:
	cd apps/api && .venv/bin/uvicorn app.main:app --reload --port 8000

web-install:
	cd apps/web && npm install

web-dev:
	cd apps/web && npm run dev

up:
	cd infra && docker compose up --build

down:
	cd infra && docker compose down
