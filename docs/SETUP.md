# Setup (Phase 0)

Prerequisites: Docker Desktop (WSL2 backend, >= 4 GB RAM for Airflow), Python 3.11+, Git.

## 1. Python environment (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```
(bash: `source .venv/bin/activate`)

## 2. Secrets
```powershell
copy .env.example .env     # then edit passwords, GITHUB_TOKEN, HTTP_CONTACT
```
`.env` is git-ignored. Generate an Airflow Fernet key if you use Airflow:
`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

## 3. Start services
```powershell
docker compose up -d --wait postgres neo4j          # core data stores
docker compose --profile airflow up -d --build --wait   # + Airflow (optional, ~4 GB RAM)
```
Endpoints: Postgres `localhost:5432`, Neo4j browser http://localhost:7474 (bolt 7687), Airflow http://localhost:8080.

## 4. Verify
```powershell
pytest
ruff check .
docker compose exec postgres psql -U patchnote -d patchnote -c "SELECT extname FROM pg_extension;"   # expect: vector
docker compose exec postgres psql -U patchnote -c "\l"                                                 # expect: airflow DB
```
Note: `docker/postgres/init/*.sql` run only on first start of an empty volume;
to re-run: `docker compose down -v` (deletes data).

## 5. Stop
`docker compose --profile airflow down`
