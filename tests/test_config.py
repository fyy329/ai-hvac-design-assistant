"""Tests for configuration behavior."""

from __future__ import annotations

import pytest

from ai_hvac.core.config import Settings
from ai_hvac.core.exceptions import ConfigurationError


class TestSettings:
    """Tests for environment-backed settings."""

    def test_openai_key_is_optional_until_requested(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(Settings.model_config, "env_file", None)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        settings = Settings()

        assert settings.openai_api_key is None
        with pytest.raises(ConfigurationError, match="OPENAI_API_KEY is required"):
            settings.get_openai_key()

    def test_openai_key_can_be_read_from_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(Settings.model_config, "env_file", None)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        settings = Settings()

        assert settings.get_openai_key() == "test-key"
