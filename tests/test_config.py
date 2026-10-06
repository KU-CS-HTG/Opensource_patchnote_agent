import json

import pytest
from pydantic import ValidationError

from patchnote.config import PackagesConfig, Settings, load_app_config, load_packages
from patchnote.logging import configure_logging, get_logger


def test_repo_packages_yaml_is_valid():
    cfg = load_packages()
    assert 1 <= len(cfg.packages) <= 5
    assert all("/" in p.github for p in cfg.packages)


def test_settings_yaml_loads():
    assert load_app_config().http.max_retries >= 1


def test_duplicate_packages_rejected():
    p = {"name": "a", "pypi": "a", "github": "o/a"}
    with pytest.raises(ValidationError):
        PackagesConfig.model_validate({"packages": [p, p]})


def test_too_many_packages_rejected():
    ps = [{"name": f"p{i}", "pypi": f"p{i}", "github": f"o/p{i}"} for i in range(6)]
    with pytest.raises(ValidationError):
        PackagesConfig.model_validate({"packages": ps})


def test_bad_github_repo_rejected():
    with pytest.raises(ValidationError):
        PackagesConfig.model_validate(
            {"packages": [{"name": "a", "pypi": "a", "github": "not-a-repo"}]}
        )


def test_settings_from_env_and_redaction(monkeypatch):
    monkeypatch.setenv("POSTGRES_PASSWORD", "s3cret")
    monkeypatch.setenv("POSTGRES_HOST", "db")
    s = Settings(_env_file=None)
    assert s.postgres_dsn == "postgresql+psycopg://patchnote:s3cret@db:5432/patchnote"
    assert "s3cret" not in repr(s)


def test_logging_emits_json(capsys):
    configure_logging("INFO")
    get_logger("t").info("hello", package="pandas")
    line = capsys.readouterr().err.strip().splitlines()[-1]
    rec = json.loads(line)
    assert rec["event"] == "hello" and rec["package"] == "pandas" and rec["level"] == "info"
