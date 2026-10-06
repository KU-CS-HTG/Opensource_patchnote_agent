"""Configuration: secrets from .env (pydantic-settings), non-secrets from config/*.yaml."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"

_GITHUB_RE = re.compile(r"^[\w.-]+/[\w.-]+$")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")

    postgres_user: str = "patchnote"
    postgres_password: str = ""
    postgres_db: str = "patchnote"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    github_token: str = ""
    http_contact: str = ""

    log_level: str = "INFO"

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    def __repr__(self) -> str:  # never leak secrets into logs
        return "Settings(<redacted>)"


class PackageSpec(BaseModel):
    name: str
    pypi: str
    github: str
    osv_ecosystem: str = "PyPI"

    @field_validator("github")
    @classmethod
    def _check_github(cls, v: str) -> str:
        if not _GITHUB_RE.match(v):
            raise ValueError(f"github must be 'owner/repo', got {v!r}")
        return v


class PackagesConfig(BaseModel):
    packages: list[PackageSpec]

    @model_validator(mode="after")
    def _unique_and_bounded(self) -> PackagesConfig:
        names = [p.name for p in self.packages]
        if len(names) != len(set(names)):
            raise ValueError("duplicate package names in packages.yaml")
        if not 1 <= len(names) <= 5:
            raise ValueError("packages.yaml must list 1..5 packages (initial scope)")
        return self


class HttpSettings(BaseModel):
    min_interval_seconds: dict[str, float] = Field(default_factory=lambda: {"default": 1.0})
    timeout_seconds: float = 30
    max_retries: int = 4
    respect_robots_txt: bool = True
    cache_dir: str = "data/http_cache"
    cache_ttl_seconds: int = 3600


class AppConfig(BaseModel):
    http: HttpSettings = Field(default_factory=HttpSettings)


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_packages(path: Path | None = None) -> PackagesConfig:
    return PackagesConfig.model_validate(_load_yaml(path or CONFIG_DIR / "packages.yaml"))


def load_app_config(path: Path | None = None) -> AppConfig:
    return AppConfig.model_validate(_load_yaml(path or CONFIG_DIR / "settings.yaml"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
