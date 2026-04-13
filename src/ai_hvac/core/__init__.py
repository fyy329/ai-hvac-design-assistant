"""Core module — configuration management and shared exceptions."""

from ai_hvac.core.config import Settings
from ai_hvac.core.exceptions import (
    AIHVACError,
    ConfigurationError,
    LLMError,
    SimulationError,
    ValidationError,
)

__all__ = [
    "Settings",
    "AIHVACError",
    "ConfigurationError",
    "LLMError",
    "SimulationError",
    "ValidationError",
]
