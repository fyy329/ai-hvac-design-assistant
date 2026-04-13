"""Rule-based HVAC system design recommender."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from ai_hvac.hvac.load_calc import ClimateZone, LoadResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SystemTemplate:
    """Static metadata for a recommendation template."""

    label: str
    components: tuple[str, ...]
    max_supply_temp: int
    renewable: bool
    typical_efficiency: float | None = None
    typical_cop: float | None = None


SYSTEM_TEMPLATES: dict[str, SystemTemplate] = {
    "gas_boiler": SystemTemplate(
        label="Condensing gas boiler",
        components=("Gas condensing boiler", "Buffer tank", "DHW tank"),
        typical_efficiency=0.96,
        max_supply_temp=80,
        renewable=False,
    ),
    "ashp": SystemTemplate(
        label="Air-source heat pump",
        components=("Air-source heat pump", "Buffer tank", "DHW tank"),
        typical_cop=3.5,
        max_supply_temp=55,
        renewable=True,
    ),
    "gshp": SystemTemplate(
        label="Ground-source heat pump",
        components=("Ground-source heat pump", "Borehole heat exchangers", "Buffer tank"),
        typical_cop=4.5,
        max_supply_temp=55,
        renewable=True,
    ),
    "ashp_gas_backup": SystemTemplate(
        label="Air-source heat pump + gas boiler backup",
        components=(
            "Air-source heat pump",
            "Gas condensing boiler (backup)",
            "Buffer tank",
            "DHW tank",
        ),
        typical_cop=3.2,
        max_supply_temp=80,
        renewable=True,
    ),
    "pvt_gshp": SystemTemplate(
        label="PVT + ground-source heat pump",
        components=(
            "PVT collectors",
            "Ground-source heat pump",
            "Borehole heat exchangers",
            "Buffer tank",
            "DHW tank",
        ),
        typical_cop=5.0,
        max_supply_temp=55,
        renewable=True,
    ),
    "district_heating": SystemTemplate(
        label="District heating connection",
        components=("District heating substation", "DHW tank"),
        typical_efficiency=0.95,
        max_supply_temp=90,
        renewable=False,
    ),
}


@dataclass
class DesignRecommendation:
    """A ranked system design recommendation."""

    rank: int = 1
    system_key: str = ""
    label: str = ""
    components: list[str] = field(default_factory=list)
    rationale: str = ""
    estimated_cop: float | None = None
    warnings: list[str] = field(default_factory=list)


class SystemDesigner:
    """Rule-based system recommender."""

    def __init__(
        self,
        climate_zone: ClimateZone,
        building_type: str,
        load_result: LoadResult,
    ) -> None:
        self.climate_zone: ClimateZone = climate_zone
        self.building_type: str = building_type.lower()
        self.load: LoadResult = load_result

    def recommend(self, *, top_n: int = 3) -> list[DesignRecommendation]:
        """Return up to *top_n* ranked system recommendations."""
        scores: list[tuple[str, float, str, list[str]]] = []
        specific = self.load.specific_load_w_per_m2

        for key, template in SYSTEM_TEMPLATES.items():
            score = 50.0
            rationale_parts: list[str] = []
            warnings: list[str] = []

            if template.renewable:
                score += 20
                rationale_parts.append("Renewable energy source preferred")

            if key == "ashp" and self.climate_zone == ClimateZone.COLD:
                score -= 15
                warnings.append("ASHP efficiency drops significantly below -5 degC")

            if key == "gshp":
                score += 10
                rationale_parts.append("Stable ground temperature provides reliable COP")

            if key == "pvt_gshp":
                score += 15
                rationale_parts.append("PVT regenerates boreholes and provides electricity")

            if specific > 80 and key in ("ashp", "gshp", "pvt_gshp"):
                score -= 10
                warning_text = (
                    f"High specific load ({specific:.0f} W/m2) - "
                    + "consider envelope improvement before heat pump"
                )
                warnings.append(warning_text)

            if specific > 100 and key == "ashp_gas_backup":
                score += 5
                rationale_parts.append("Gas backup covers peak load efficiently")

            if self.building_type in {"office", "school"} and key in ("ashp", "gshp", "pvt_gshp"):
                score += 5
                rationale_parts.append("Low-temperature emitters are common in this building type")

            if self.building_type == "hospital":
                if key in ("gas_boiler", "ashp_gas_backup", "district_heating"):
                    score += 10
                    rationale_parts.append(
                        "High DHW and temperature lift suit robust backup capacity"
                    )
                if key in ("ashp", "gshp", "pvt_gshp"):
                    score -= 20
                    warnings.append("Check DHW peak demand and supply temperatures carefully")

            if self.load.total_heating_load_kw > 200 and key == "district_heating":
                score += 15
                rationale_parts.append("Large load suits district heating connection")

            scores.append((key, score, "; ".join(dict.fromkeys(rationale_parts)), warnings))

        scores.sort(key=lambda item: item[1], reverse=True)

        recommendations: list[DesignRecommendation] = []
        for rank, (key, _score, rationale, warnings) in enumerate(scores[:top_n], start=1):
            template = SYSTEM_TEMPLATES[key]
            estimated_cop = template.typical_cop
            if estimated_cop is None:
                estimated_cop = template.typical_efficiency
            recommendations.append(
                DesignRecommendation(
                    rank=rank,
                    system_key=key,
                    label=template.label,
                    components=list(template.components),
                    rationale=rationale,
                    estimated_cop=estimated_cop,
                    warnings=warnings,
                )
            )

        logger.info("Generated %d system recommendations", len(recommendations))
        return recommendations
