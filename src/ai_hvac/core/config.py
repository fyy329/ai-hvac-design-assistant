"""
Application configuration powered by pydantic-settings.

Settings are loaded from environment variables and/or a `.env` file.
See `.env.example` for the full list of recognised variables.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings.

    Attributes
    ----------
    openai_api_key : SecretStr
        OpenAI API key (loaded from ``OPENAI_API_KEY``).
    openai_model : str
        Chat-completion model to use (default ``gpt-4o``).
    openai_max_tokens : int
        Maximum tokens per completion response.
    openai_temperature : float
        Sampling temperature for completions.
    log_level : str
        Logging verbosity (``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``).
    cache_dir : Path
        Directory for caching LLM responses and intermediate results.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # -- OpenAI --
    openai_api_key: SecretStr = Field(
        ...,
        description="OpenAI API key",
    )
    openai_model: str = Field(
        default="gpt-4o",
        description="Model identifier for chat completions",
    )
    openai_max_tokens: int = Field(
        default=4096,
        ge=1,
        le=128_000,
        description="Maximum tokens per response",
    )
    openai_temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        description="Sampling temperature",
    )

    # -- Application --
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
    )
    cache_dir: Path = Field(
        default=Path(".cache"),
        description="Directory for caching intermediate results",
    )

    # -- Convenience helpers --
    def get_openai_key(self) -> str:
        """Return the plain-text API key (use sparingly)."""
        return self.openai_api_key.get_secret_value()
