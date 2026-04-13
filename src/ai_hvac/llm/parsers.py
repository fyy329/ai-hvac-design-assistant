"""Parsers for extracting structured data from LLM responses."""

from __future__ import annotations

import json
import re
from typing import Any

from ai_hvac.core.exceptions import LLMError


def extract_json(text: str) -> dict[str, Any]:
    """Extract the first JSON object from *text*."""
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\n?```\s*$", "", cleaned.strip(), flags=re.MULTILINE)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match is None:
            raise LLMError("No JSON object found in LLM response") from None
        try:
            data = json.loads(match.group())
        except json.JSONDecodeError as exc:
            raise LLMError(f"Failed to parse JSON from LLM response: {exc}") from exc

    if not isinstance(data, dict):
        raise LLMError(f"Expected a JSON object, got {type(data).__name__}")
    return data


def safe_float(value: Any, default: float | None = 0.0) -> float | None:
    """Coerce *value* to ``float``, falling back to *default*."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_list(value: Any) -> list[str]:
    """Ensure *value* is a list of strings."""
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        return [value]
    return []
