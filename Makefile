# On Windows without make, run the commands in docs/SETUP.md directly.
.PHONY: install up up-airflow down test lint
install:
	python -m venv .venv && .venv/bin/pip install -e ".[dev]"
up:
	docker compose up -d --wait postgres neo4j
up-airflow:
	docker compose --profile airflow up -d --build --wait
down:
	docker compose --profile airflow down
test:
	pytest
lint:
	ruff check .
