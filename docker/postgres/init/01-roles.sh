#!/bin/bash
# Runs once on first start of an empty data volume, as the bootstrap superuser.
# Creates least-privilege roles. Passwords come from container env (from .env), never from files.
set -euo pipefail

: "${DB_OWNER_USER:?}" "${DB_OWNER_PASSWORD:?}" "${DB_COLLECTOR_USER:?}" "${DB_COLLECTOR_PASSWORD:?}"
: "${DB_READER_USER:?}" "${DB_READER_PASSWORD:?}" "${AIRFLOW_DB_USER:?}" "${AIRFLOW_DB_PASSWORD:?}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  -v owner="$DB_OWNER_USER"         -v owner_pw="$DB_OWNER_PASSWORD" \
  -v collector="$DB_COLLECTOR_USER" -v collector_pw="$DB_COLLECTOR_PASSWORD" \
  -v reader="$DB_READER_USER"       -v reader_pw="$DB_READER_PASSWORD" \
  -v airflow="$AIRFLOW_DB_USER"     -v airflow_pw="$AIRFLOW_DB_PASSWORD" \
  -v appdb="$POSTGRES_DB" <<'SQL'
-- Roles (no superuser, no createdb/createrole)
CREATE ROLE :"owner"     LOGIN PASSWORD :'owner_pw'     NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE :"collector" LOGIN PASSWORD :'collector_pw' NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE :"reader"    LOGIN PASSWORD :'reader_pw'    NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE :"airflow"   LOGIN PASSWORD :'airflow_pw'   NOSUPERUSER NOCREATEDB NOCREATEROLE;

-- Lock down defaults
REVOKE ALL ON DATABASE :"appdb" FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT CONNECT ON DATABASE :"appdb" TO :"owner", :"collector", :"reader";

-- Extensions need superuser: install here, once
CREATE EXTENSION IF NOT EXISTS vector;

-- Schemas: raw = collected originals (collector writes), core = parsed/extracted data
CREATE SCHEMA raw  AUTHORIZATION :"owner";
CREATE SCHEMA core AUTHORIZATION :"owner";

-- collector: insert/update raw only; no DELETE, no access to core
GRANT USAGE ON SCHEMA raw TO :"collector";
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA raw
  GRANT SELECT, INSERT, UPDATE ON TABLES TO :"collector";
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA raw
  GRANT USAGE, SELECT ON SEQUENCES TO :"collector";

-- reader: select on everything the owner creates
GRANT USAGE ON SCHEMA raw, core TO :"reader";
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA raw  GRANT SELECT ON TABLES TO :"reader";
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA core GRANT SELECT ON TABLES TO :"reader";

-- Airflow metadata lives in its own database, owned by its own role
CREATE DATABASE airflow OWNER :"airflow";
REVOKE ALL ON DATABASE airflow FROM PUBLIC;
SQL
