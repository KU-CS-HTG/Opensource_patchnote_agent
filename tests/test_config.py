import json

import pytest
from pydantic import ValidationError

from opsgraph.config import (
    ModelsConfig,
    Settings,
    SourcesConfig,
    load_app_config,
    load_models,
    load_sources,
)
from opsgraph.logging import configure_logging, get_logger


def test_repo_configs_load():
    assert load_sources().sources == []  # nothing approved yet
    assert load_app_config().http.max_retries >= 1
    m = load_models()
    assert m.embedding.provider == "local" and m.llm.provider == "local"
    assert m.allow_external is False


def test_unapproved_source_is_refused():
    with pytest.raises(KeyError):
        SourcesConfig().get("nvd")


def test_conditional_source_needs_conditions():
    with pytest.raises(ValidationError):
        SourcesConfig.model_validate({"sources": [{"id": "x", "status": "conditional"}]})


def test_duplicate_source_ids_rejected():
    s = {"id": "x", "status": "approved"}
    with pytest.raises(ValidationError):
        SourcesConfig.model_validate({"sources": [s, s]})


def test_external_provider_requires_opt_in():
    with pytest.raises(ValidationError):
        ModelsConfig.model_validate({"embedding": {"provider": "api"}})
    ok = ModelsConfig.model_validate({"allow_external": True, "llm": {"provider": "api"}})
    assert ok.llm.provider == "api"


def test_dsn_uses_role_credentials_and_hides_secrets(monkeypatch):
    monkeypatch.setenv("DB_READER_PASSWORD", "s3cret")
    monkeypatch.setenv("POSTGRES_HOST", "db")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.delenv("DB_READER_USER", raising=False)
    s = Settings(_env_file=None)
    assert s.dsn("reader") == "postgresql://og_reader:s3cret@db:5432/opsgraph"
    assert s.dsn("collector").startswith("postgresql://og_collector:")
    assert "s3cret" not in repr(s)


def test_logging_emits_json(capsys):
    configure_logging("INFO")
    get_logger("t").info("hello", source="nvd")
    rec = json.loads(capsys.readouterr().err.strip().splitlines()[-1])
    assert rec["event"] == "hello" and rec["source"] == "nvd" and rec["level"] == "info"
