"""
AI-augmented HVAC system design recommender.

Combines rule-based heuristics with LLM-powered suggestions to propose
heating/cooling system configurations for a given building.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ai_hvac.hvac.load_calc import ClimateZone, LoadResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# System taxonomy
# ---------------------------------------------------------------------------

SYSTEM_TEMPLATES: dict[str, dict[str, Any]] = {
    "gas_boiler": {
        "label": "Condensing gas boiler",
        "components": ["Gas condensing boiler", "Buffer tank", "DHW tank"],
        "typical_efficiency": 0.96,
        "max_supply_temp": 80,
        "renewable": False,
    },
    "ashp": {
        "label": "Air-source heat pump",
        "components": ["Air-source heat pump", "Buffer tank", "DHW tank"],
        "typical_cop": 3.5,
        "max_supply_temp": 55,
        "renewable": True,
    },
    "gshp": {
        "label": "Ground-source heat pump",
        "components": ["Ground-source heat pump", "Borehole heat exchangers", "Buffer tank"],
        "typical_cop": 4.5,
        "max_supply_temp": 55,
        "renewable": True,
    },
    "ashp_gas_backup": {
        "label": "Air-source heat pump + gas boiler backup",
        "components": [
            "Air-source heat pump",
            "Gas condensing boiler (backup)",
            "Buffer tank",
            "DHW tank",
        ],
        "typical_cop": 3.2,
        "max_supply_temp": 80,
        "renewable": True,
    },
    "pvt_gshp": {
        "label": "PVT + ground-source heat pump",
        "components": [
            "PVT collectors",
            "Ground-source heat pump",
            "Borehole heat exchangers",
            "Buffer tank",
            "DHW tank",
        ],
        "typical_cop": 5.0,
        "max_supply_temp": 55,
        "renewable": True,
    },
    "district_heating": {
        "label": "District heating connection",
        "components": ["District heating substation", "DHW tank"],
        "typical_efficiency": 0.95,
        "max_supply_temp": 90,
        "renewable": False,  # depends on source
    },
}


# ---------------------------------------------------------------------------
# Recommendation data class
# ---------------------------------------------------------------------------

@dataclass
class DesignRecommendation:
    """A ranked system design recommendation.

    Attributes
    ----------
    rank : int
        Priority rank (1 = best fit).
    system_key : str
        Key into ``SYSTEM_TEMPLATES``.
    label : str
        Human-readable system name.
    components : list[str]
        Major equipment items.
    rationale : str
        Engineering reasoning for this recommendation.
    estimated_cop : float | None
        Seasonal COP / efficiency estimate.
    warnings : list[str]
        Caveats or risks.
    """

    rank: int = 1
    system_key: str = ""
    label: str = ""
    components: list[str] = field(default_factory=list)
    rationale: str = ""
    estimated_cop: float | None = None
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Rule-based recommender
# ---------------------------------------------------------------------------

class SystemDesigner:
    """Rule-based system recommender (no LLM dependency).

    For AI-augmented recommendations, use
    :meth:`~ai_hvac.llm.client.HVACAssistant.recommend_system` instead.

    Parameters
    ----------
    climate_zone : ClimateZone
        Building climate zone.
    building_type : str
        Building usage type.
    load_result : LoadResult
        Result from a previous load calculation.
    """

    def __init__(
        self,
        climate_zone: ClimateZone,
        building_type: str,
        load_result: LoadResult,
    ) -> None:
        self.climate_zone = climate_zone
        self.building_type = building_type.lower()
        self.load = load_result

    def recommend(self, *, top_n: int = 3) -> list[DesignRecommendation]:
        """Return up to *top_n* ranked system recommendations.

        The ranking heuristic considers climate severity, load density,
        and building type.

        Returns
        -------
        list[DesignRecommendation]
        """
        scores: list[tuple[str, float, str, list[str]]] = []

        specific = self.load.specific_load_w_per_m2

        for key, tmpl in SYSTEM_TEMPLATES.items():
            score = 50.0  # base score
            rationale_parts: list[str] = []
            warnings: list[str] = []

            # Prefer renewable systems
            if tmpl.get("renewable"):
                score += 20
                rationale_parts.append("Renewable energy source preferred")

            # Climate suitability
            if key == "ashp" and self.climate_zone == ClimateZone.COLD:
                score -= 15
                warnings.append("ASHP efficiency drops significantly below −15 °C")

            if key == "gshp":
                score += 10  # stable performance
                rationale_parts.append("Stable ground temperature provides reliable COP")

            if key == "pvt_gshp":
                score += 15
                rationale_parts.append("PVT regenerates boreholes and provides electricity")

            # Load density suitability
            if specific > 80 and key in ("ashp", "gshp", "pvt_gshp"):
                score -= 10
                warnings.append(
                    f"High specific load ({specific:.0f} W/m²) — "
                    "consider envelope improvement before heat pump"
                )

            if specific > 100 and key == "ashp_gas_backup":
                score += 5
                rationale_parts.append("Gas backup covers peak load efficiently")

            # District heating for large buildings
            if self.load.total_heating_load_kw > 200 and key == "district_heating":
                score += 15
                rationale_parts.append("Large load suits district heating connection")

            scores.append((key, score, "; ".join(rationale_parts), warnings))

        # Sort by descending score
        scores.sort(key=lambda x: x[1], reverse=True)

        recommendations = []
        for rank, (key, _score, rationale, warnings) in enumerate(scores[:top_n], start=1):
            tmpl = SYSTEM_TEMPLATES[key]
            recommendations.append(
                DesignRecommendation(
                    rank=rank,
                    system_key=key,
                    label=tmpl["label"],
                    components=list(tmpl["components"]),
                    rationale=rationale,
                    estimated_cop=tmpl.get("typical_cop") or tmpl.get("typical_efficiency"),
                    warnings=warnings,
                )
            )

        logger.info("Generated %d system recommendations", len(recommendations))
        return recommendations
