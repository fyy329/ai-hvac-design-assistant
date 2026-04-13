"""OpenAI API client tailored for HVAC engineering tasks."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.shared_params import ResponseFormatJSONObject

from ai_hvac.core.config import Settings
from ai_hvac.core.exceptions import LLMError
from ai_hvac.llm.parsers import extract_json, safe_float, safe_list
from ai_hvac.llm.prompts import PromptLibrary

logger = logging.getLogger(__name__)
JSON_RESPONSE_FORMAT: ResponseFormatJSONObject = {"type": "json_object"}


@dataclass
class SystemRecommendation:
    """Structured result from an AI system-design query."""

    system_type: str
    components: list[str] = field(default_factory=list)
    estimated_cop: float | None = None
    rationale: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass
class LoadEstimate:
    """AI-assisted load-estimation result."""

    heating_load_kw: float
    cooling_load_kw: float | None = None
    assumptions: list[str] = field(default_factory=list)
    confidence: str = "medium"


class HVACAssistant:
    """High-level AI assistant for HVAC design tasks."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings: Settings = settings if settings is not None else Settings()
        self._client: OpenAI = OpenAI(api_key=self._settings.get_openai_key())
        self._prompts: PromptLibrary = PromptLibrary()

    def recommend_system(
        self,
        building_type: str,
        location: str,
        heated_area_m2: float,
        *,
        cooling_required: bool = False,
        dhw_required: bool = True,
        additional_context: str = "",
    ) -> SystemRecommendation:
        """Ask the LLM to recommend an HVAC system configuration."""
        user_prompt = self._prompts.system_recommendation(
            building_type=building_type,
            location=location,
            heated_area_m2=heated_area_m2,
            cooling_required=cooling_required,
            dhw_required=dhw_required,
            additional_context=additional_context,
        )
        raw = self._chat(
            system=self._prompts.SYSTEM_ENGINEER,
            user=user_prompt,
            response_format=JSON_RESPONSE_FORMAT,
        )
        return self._parse_recommendation(raw)

    def estimate_loads(
        self,
        building_type: str,
        location: str,
        heated_area_m2: float,
        *,
        u_values: dict[str, float] | None = None,
        ventilation_rate: float | None = None,
    ) -> LoadEstimate:
        """Use AI to estimate heating and cooling loads."""
        user_prompt = self._prompts.load_estimation(
            building_type=building_type,
            location=location,
            heated_area_m2=heated_area_m2,
            u_values=u_values,
            ventilation_rate=ventilation_rate,
        )
        raw = self._chat(
            system=self._prompts.SYSTEM_ENGINEER,
            user=user_prompt,
            response_format=JSON_RESPONSE_FORMAT,
        )
        return self._parse_load_estimate(raw)

    def ask(self, question: str) -> str:
        """Free-form Q&A with HVAC-domain context."""
        return self._chat(
            system=self._prompts.SYSTEM_ENGINEER,
            user=question,
        )

    def _chat(
        self,
        system: str,
        user: str,
        *,
        response_format: ResponseFormatJSONObject | None = None,
    ) -> str:
        """Send a single chat-completion request and return the content."""
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        logger.debug("Sending chat-completion request (model=%s)", self._settings.openai_model)
        try:
            if response_format is None:
                response = self._client.chat.completions.create(
                    model=self._settings.openai_model,
                    messages=messages,
                    max_tokens=self._settings.openai_max_tokens,
                    temperature=self._settings.openai_temperature,
                )
            else:
                response = self._client.chat.completions.create(
                    model=self._settings.openai_model,
                    messages=messages,
                    max_tokens=self._settings.openai_max_tokens,
                    temperature=self._settings.openai_temperature,
                    response_format=response_format,
                )
        except Exception as exc:
            raise LLMError(f"OpenAI API call failed: {exc}") from exc

        content = response.choices[0].message.content
        if not isinstance(content, str):
            raise LLMError("LLM returned an empty response")
        return content

    @staticmethod
    def _parse_recommendation(raw: str) -> SystemRecommendation:
        """Parse a JSON response into a ``SystemRecommendation``."""
        data = extract_json(raw)
        return SystemRecommendation(
            system_type=str(data.get("system_type", "unknown")),
            components=safe_list(data.get("components")),
            estimated_cop=safe_float(data.get("estimated_cop"), default=None),
            rationale=str(data.get("rationale", "")),
            warnings=safe_list(data.get("warnings")),
        )

    @staticmethod
    def _parse_load_estimate(raw: str) -> LoadEstimate:
        """Parse a JSON response into a ``LoadEstimate``."""
        data = extract_json(raw)
        heating_load = safe_float(data.get("heating_load_kw"), default=0.0)
        return LoadEstimate(
            heating_load_kw=float(heating_load if heating_load is not None else 0.0),
            cooling_load_kw=safe_float(data.get("cooling_load_kw"), default=None),
            assumptions=safe_list(data.get("assumptions")),
            confidence=str(data.get("confidence", "medium")),
        )
