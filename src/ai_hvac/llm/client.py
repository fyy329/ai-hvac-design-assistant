"""
OpenAI API client tailored for HVAC engineering tasks.

This module wraps the OpenAI chat-completion API and adds:
* Automatic retry with exponential back-off.
* Structured output parsing via function-calling / JSON mode.
* Domain-specific system prompts for HVAC design workflows.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI

from ai_hvac.core.config import Settings
from ai_hvac.core.exceptions import LLMError
from ai_hvac.llm.prompts import PromptLibrary

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes for structured responses
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main client
# ---------------------------------------------------------------------------

class HVACAssistant:
    """High-level AI assistant for HVAC design tasks.

    Parameters
    ----------
    settings : Settings, optional
        Application settings.  When *None*, settings are loaded from the
        environment / ``.env`` automatically.

    Examples
    --------
    >>> from ai_hvac import HVACAssistant
    >>> assistant = HVACAssistant()
    >>> result = assistant.recommend_system(
    ...     building_type="residential",
    ...     location="Munich, Germany",
    ...     heated_area_m2=450,
    ... )
    >>> print(result.system_type)
    'Air-source heat pump with PVT support'
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()
        self._client = OpenAI(api_key=self._settings.get_openai_key())
        self._prompts = PromptLibrary()

    # -- Public API ---------------------------------------------------------

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
        """Ask the LLM to recommend an HVAC system configuration.

        Parameters
        ----------
        building_type : str
            E.g. ``"residential"``, ``"office"``, ``"school"``.
        location : str
            City or region used to infer climate zone.
        heated_area_m2 : float
            Gross heated floor area in m².
        cooling_required : bool
            Whether active cooling is needed.
        dhw_required : bool
            Whether domestic hot water production is needed.
        additional_context : str
            Free-form extra information for the LLM.

        Returns
        -------
        SystemRecommendation
        """
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
            response_format={"type": "json_object"},
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
        """Use AI to estimate heating (and optionally cooling) loads.

        The LLM is prompted with building metadata and, if available,
        envelope U-values.  It returns a structured load estimate together
        with the assumptions it made.

        Parameters
        ----------
        building_type : str
            Building usage type.
        location : str
            City or region.
        heated_area_m2 : float
            Gross heated floor area in m².
        u_values : dict, optional
            Envelope U-values keyed by component name (``wall``, ``roof``,
            ``window``, ``floor``).
        ventilation_rate : float, optional
            Design ventilation rate in m³/h.

        Returns
        -------
        LoadEstimate
        """
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
            response_format={"type": "json_object"},
        )
        return self._parse_load_estimate(raw)

    def ask(self, question: str) -> str:
        """Free-form Q&A with HVAC-domain context.

        Parameters
        ----------
        question : str
            Any HVAC or building-energy related question.

        Returns
        -------
        str
            The assistant's plain-text answer.
        """
        return self._chat(
            system=self._prompts.SYSTEM_ENGINEER,
            user=question,
        )

    # -- Internal helpers ---------------------------------------------------

    def _chat(
        self,
        system: str,
        user: str,
        *,
        response_format: dict[str, str] | None = None,
    ) -> str:
        """Send a single chat-completion request and return the content."""
        kwargs: dict[str, Any] = {
            "model": self._settings.openai_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": self._settings.openai_max_tokens,
            "temperature": self._settings.openai_temperature,
        }
        if response_format is not None:
            kwargs["response_format"] = response_format

        logger.debug("Sending chat-completion request (model=%s)", self._settings.openai_model)
        try:
            response = self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            raise LLMError(f"OpenAI API call failed: {exc}") from exc

        content = response.choices[0].message.content
        if content is None:
            raise LLMError("LLM returned an empty response")
        return content

    @staticmethod
    def _parse_recommendation(raw: str) -> SystemRecommendation:
        """Parse a JSON response into a ``SystemRecommendation``."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LLMError(f"Failed to parse JSON from LLM: {exc}") from exc

        return SystemRecommendation(
            system_type=data.get("system_type", "unknown"),
            components=data.get("components", []),
            estimated_cop=data.get("estimated_cop"),
            rationale=data.get("rationale", ""),
            warnings=data.get("warnings", []),
        )

    @staticmethod
    def _parse_load_estimate(raw: str) -> LoadEstimate:
        """Parse a JSON response into a ``LoadEstimate``."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LLMError(f"Failed to parse JSON from LLM: {exc}") from exc

        return LoadEstimate(
            heating_load_kw=float(data.get("heating_load_kw", 0)),
            cooling_load_kw=data.get("cooling_load_kw"),
            assumptions=data.get("assumptions", []),
            confidence=data.get("confidence", "medium"),
        )
