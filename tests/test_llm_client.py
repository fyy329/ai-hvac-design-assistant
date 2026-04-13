"""Tests for the LLM client (mocked — no real API calls)."""

from __future__ import annotations

import json

import pytest

from ai_hvac.llm.client import HVACAssistant, LoadEstimate, SystemRecommendation
from ai_hvac.llm.parsers import extract_json, safe_float, safe_list

# ---------------------------------------------------------------------------
# Parser tests (no mocking needed)
# ---------------------------------------------------------------------------

class TestExtractJson:
    """Tests for the JSON extraction helper."""

    def test_plain_json(self) -> None:
        text = '{"heating_load_kw": 25.5, "confidence": "high"}'
        result = extract_json(text)
        assert result["heating_load_kw"] == 25.5

    def test_json_with_markdown_fences(self) -> None:
        text = '```json\n{"system_type": "heat pump"}\n```'
        result = extract_json(text)
        assert result["system_type"] == "heat pump"

    def test_json_embedded_in_text(self) -> None:
        text = 'Here is my answer:\n{"a": 1, "b": 2}\nHope this helps!'
        result = extract_json(text)
        assert result["a"] == 1

    def test_invalid_json_raises(self) -> None:
        from ai_hvac.core.exceptions import LLMError

        with pytest.raises(LLMError):
            extract_json("This is not JSON at all.")


class TestSafeFloat:
    def test_valid_float(self) -> None:
        assert safe_float(3.14) == 3.14

    def test_string_number(self) -> None:
        assert safe_float("42") == 42.0

    def test_none_returns_default(self) -> None:
        assert safe_float(None, default=0.0) == 0.0

    def test_garbage_returns_default(self) -> None:
        assert safe_float("not_a_number", default=-1.0) == -1.0


class TestSafeList:
    def test_list_of_strings(self) -> None:
        assert safe_list(["a", "b"]) == ["a", "b"]

    def test_single_string(self) -> None:
        assert safe_list("hello") == ["hello"]

    def test_none(self) -> None:
        assert safe_list(None) == []


# ---------------------------------------------------------------------------
# Client tests (mocked OpenAI)
# ---------------------------------------------------------------------------

class TestHVACAssistantParsing:
    """Test the parsing logic of HVACAssistant without real API calls."""

    def test_parse_recommendation(self) -> None:
        raw = json.dumps({
            "system_type": "Air-source heat pump",
            "components": ["ASHP", "Buffer tank", "DHW tank"],
            "estimated_cop": 3.5,
            "rationale": "Good fit for moderate climate",
            "warnings": ["Noise level may be an issue"],
        })
        result = HVACAssistant._parse_recommendation(raw)
        assert isinstance(result, SystemRecommendation)
        assert result.system_type == "Air-source heat pump"
        assert result.estimated_cop == 3.5
        assert len(result.components) == 3

    def test_parse_load_estimate(self) -> None:
        raw = json.dumps({
            "heating_load_kw": 28.5,
            "cooling_load_kw": None,
            "assumptions": ["U-wall = 0.28 assumed"],
            "confidence": "medium",
        })
        result = HVACAssistant._parse_load_estimate(raw)
        assert isinstance(result, LoadEstimate)
        assert result.heating_load_kw == 28.5
        assert result.cooling_load_kw is None
        assert result.confidence == "medium"
