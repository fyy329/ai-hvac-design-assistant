"""
Custom exception hierarchy for AI HVAC Design Assistant.

All domain exceptions inherit from :class:`AIHVACError` so callers can
catch a single base class when they want to handle *any* library error.
"""

from __future__ import annotations


class AIHVACError(Exception):
    """Base exception for the ai-hvac library."""


class ConfigurationError(AIHVACError):
    """Raised when required configuration is missing or invalid."""


class LLMError(AIHVACError):
    """Raised when an LLM API call fails or returns unparseable output."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ValidationError(AIHVACError):
    """Raised when user-supplied input fails validation."""


class SimulationError(AIHVACError):
    """Raised when simulation template generation or execution fails."""
