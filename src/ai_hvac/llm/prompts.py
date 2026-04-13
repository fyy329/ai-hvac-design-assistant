"""
HVAC-domain prompt templates.

Every prompt is designed to produce *structured JSON* so that downstream
parsers can extract actionable engineering data from LLM responses.
"""

from __future__ import annotations


class PromptLibrary:
    """Collection of domain-specific prompt templates for HVAC tasks."""

    # -- System prompts -----------------------------------------------------

    SYSTEM_ENGINEER: str = (
        "You are a senior HVAC and building energy systems engineer with 20 years "
        "of experience.  You are precise, reference DIN/EN/ASHRAE standards where "
        "applicable, and always provide quantitative reasoning.  When asked for a "
        "system design, you consider climate, envelope quality, occupancy, DHW "
        "demand, and local energy prices.  You communicate clearly and "
        "professionally."
    )

    # -- User prompt builders -----------------------------------------------

    @staticmethod
    def system_recommendation(
        building_type: str,
        location: str,
        heated_area_m2: float,
        *,
        cooling_required: bool = False,
        dhw_required: bool = True,
        additional_context: str = "",
    ) -> str:
        """Build a user prompt for HVAC system recommendation.

        Returns a prompt that instructs the LLM to reply in JSON with keys:
        ``system_type``, ``components``, ``estimated_cop``, ``rationale``,
        ``warnings``.
        """
        parts = [
            "Recommend an HVAC system configuration for the following building.",
            "",
            f"- **Building type**: {building_type}",
            f"- **Location**: {location}",
            f"- **Heated floor area**: {heated_area_m2} m²",
            f"- **Cooling required**: {'yes' if cooling_required else 'no'}",
            f"- **DHW required**: {'yes' if dhw_required else 'no'}",
        ]
        if additional_context:
            parts.append(f"- **Additional context**: {additional_context}")

        parts += [
            "",
            "Reply in **JSON** with the following keys:",
            "  - `system_type` (string): e.g. 'Air-source heat pump with gas boiler backup'",
            "  - `components` (list of strings): major equipment items",
            "  - `estimated_cop` (number or null): seasonal COP estimate",
            "  - `rationale` (string): brief engineering rationale",
            "  - `warnings` (list of strings): any caveats or risks",
        ]
        return "\n".join(parts)

    @staticmethod
    def load_estimation(
        building_type: str,
        location: str,
        heated_area_m2: float,
        *,
        u_values: dict[str, float] | None = None,
        ventilation_rate: float | None = None,
    ) -> str:
        """Build a user prompt for heating/cooling load estimation.

        Returns a prompt that instructs the LLM to reply in JSON with keys:
        ``heating_load_kw``, ``cooling_load_kw``, ``assumptions``,
        ``confidence``.
        """
        parts = [
            "Estimate the design heating load (and cooling load if applicable) "
            "for the following building.  Use DIN EN 12831 methodology where possible.",
            "",
            f"- **Building type**: {building_type}",
            f"- **Location**: {location}",
            f"- **Heated floor area**: {heated_area_m2} m²",
        ]
        if u_values:
            parts.append("- **Envelope U-values (W/m²K)**:")
            for component, value in u_values.items():
                parts.append(f"    - {component}: {value}")
        if ventilation_rate is not None:
            parts.append(f"- **Design ventilation rate**: {ventilation_rate} m³/h")

        parts += [
            "",
            "Reply in **JSON** with the following keys:",
            "  - `heating_load_kw` (number): peak heating load in kW",
            "  - `cooling_load_kw` (number or null): peak cooling load in kW",
            "  - `assumptions` (list of strings): key assumptions you made",
            "  - `confidence` (string): 'low', 'medium', or 'high'",
        ]
        return "\n".join(parts)

    @staticmethod
    def polysun_template(
        system_type: str,
        components: list[str],
        heated_area_m2: float,
        dhw_demand_litres_day: float = 0,
    ) -> str:
        """Build a prompt for generating Polysun simulation parameters.

        The LLM is asked to return a JSON object that can seed a Polysun
        project template.
        """
        parts = [
            "Generate a Polysun simulation setup for the following HVAC system.",
            "",
            f"- **System type**: {system_type}",
            f"- **Components**: {', '.join(components)}",
            f"- **Heated area**: {heated_area_m2} m²",
            f"- **DHW demand**: {dhw_demand_litres_day} litres/day",
            "",
            "Reply in **JSON** with the following structure:",
            "  - `template_name` (string)",
            "  - `heat_generator` (object with `type`, `nominal_power_kw`, `cop`)",
            "  - `storage` (object with `volume_litres`, `type`)",
            "  - `solar_thermal` (object or null with `type`, `area_m2`, `orientation`)",
            "  - `control_strategy` (string): brief description of control logic",
            "  - `notes` (list of strings): tips for manual adjustment in the GUI",
        ]
        return "\n".join(parts)
