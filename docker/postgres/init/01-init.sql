-- Runs once on first container start (empty data volume).
-- App DB is POSTGRES_DB; Airflow metadata lives in a separate DB.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE DATABASE airflow;
