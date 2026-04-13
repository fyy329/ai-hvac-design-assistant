"""
Parsers for extracting structured data from LLM responses.

These helpers complement the JSON-mode parsing in :mod:`ai_hvac.llm.client`
by providing additional validation and normalisation steps.
"""

from __future__ import annotations

import json
import re
from typing import Any

from ai_hvac.core.exceptions import LLMError


def extract_json(text: str) -> dict[str, Any]:
    """Extract the first JSON object from *text*.

    The LLM sometimes wraps JSON in markdown code fences (````json … ````).
    This function strips those fences before parsing.

    Parameters
    ----------
    text : str
        Raw LLM output.

    Returns
    -------
    dict
        Parsed JSON object.

    Raises
    ------
    LLMError
        If no valid JSON object can be found.
    """
    # Strip optional markdown code fences
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\n?```\s*$", "", cleaned.strip(), flags=re.MULTILINE)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fall back: try to find the first { ... } block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match is None:
            raise LLMError("No JSON object found in LLM response")
        try:
            data = json.loads(match.group())
        except json.JSONDecodeError as exc:
            raise LLMError(f"Failed to parse JSON from LLM response: {exc}") from exc

    if not isinstance(data, dict):
        raise LLMError(f"Expected a JSON object, got {type(data).__name__}")
    return data


def safe_float(value: Any, default: float = 0.0) -> float:
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
