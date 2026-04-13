"""
Simplified heating and cooling load calculator.

Implements a *static* method based on DIN EN 12831 (simplified) for
quick design-stage estimates.  For full compliance, a dedicated tool
such as nPro or a certified BIM plugin should be used.

The calculator can optionally be augmented with AI suggestions for
missing parameters (e.g. U-values, infiltration rates) via the
:class:`~ai_hvac.llm.client.HVACAssistant`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

class ClimateZone(Enum):
    """Simplified climate zones (based on DIN EN 12831 outdoor design temps)."""

    COLD = "cold"            # e.g. Scandinavia, −20 °C
    MODERATE_COLD = "moderate_cold"  # e.g. Central Europe, −12 °C
    MODERATE = "moderate"    # e.g. Western Europe, −5 °C
    MILD = "mild"            # e.g. Southern Europe, 0 °C

    @property
    def design_outdoor_temp(self) -> float:
        """Return the outdoor design temperature in °C."""
        return {
            ClimateZone.COLD: -20.0,
            ClimateZone.MODERATE_COLD: -12.0,
            ClimateZone.MODERATE: -5.0,
            ClimateZone.MILD: 0.0,
        }[self]


#: Default U-values (W/m²K) per building age class.
DEFAULT_U_VALUES: dict[str, dict[str, float]] = {
    "pre_1980": {"wall": 1.4, "roof": 0.9, "floor": 1.0, "window": 2.8},
    "1980_2000": {"wall": 0.6, "roof": 0.4, "floor": 0.5, "window": 1.8},
    "post_2000": {"wall": 0.28, "roof": 0.20, "floor": 0.35, "window": 1.3},
    "passive_house": {"wall": 0.15, "roof": 0.10, "floor": 0.15, "window": 0.80},
}

#: Typical internal gains (W/m²).
INTERNAL_GAINS: dict[str, float] = {
    "residential": 5.0,
    "office": 15.0,
    "school": 10.0,
    "retail": 12.0,
    "hospital": 18.0,
}

#: Typical room set-point temperatures (°C).
SETPOINT_TEMP: dict[str, float] = {
    "residential": 20.0,
    "office": 21.0,
    "school": 20.0,
    "hospital": 22.0,
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class EnvelopeSpec:
    """Building envelope specification.

    Attributes
    ----------
    wall_area_m2 : float
        Total external wall area (excluding windows).
    roof_area_m2 : float
        Roof area.
    floor_area_m2 : float
        Ground-contact floor area.
    window_area_m2 : float
        Total window / glazing area.
    u_wall, u_roof, u_floor, u_window : float
        Thermal transmittance values in W/(m²·K).
    """

    wall_area_m2: float
    roof_area_m2: float
    floor_area_m2: float
    window_area_m2: float
    u_wall: float = 0.28
    u_roof: float = 0.20
    u_floor: float = 0.35
    u_window: float = 1.3


@dataclass
class LoadResult:
    """Result of a heating/cooling load calculation.

    Attributes
    ----------
    transmission_loss_w : float
        Heat loss through the building envelope.
    ventilation_loss_w : float
        Heat loss due to air exchange.
    total_heating_load_w : float
        Peak design heating load.
    specific_load_w_per_m2 : float
        Heating load normalised to heated floor area.
    assumptions : list[str]
        Plain-language list of assumptions made.
    """

    transmission_loss_w: float = 0.0
    ventilation_loss_w: float = 0.0
    total_heating_load_w: float = 0.0
    specific_load_w_per_m2: float = 0.0
    assumptions: list[str] = field(default_factory=list)

    @property
    def total_heating_load_kw(self) -> float:
        """Total heating load in kW."""
        return self.total_heating_load_w / 1000.0


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------

class HeatingLoadCalculator:
    """Simplified heating load calculator (DIN EN 12831 approach).

    Parameters
    ----------
    climate_zone : ClimateZone
        Outdoor design climate zone.
    building_type : str
        Building usage type (``residential``, ``office``, etc.).
    heated_area_m2 : float
        Gross heated floor area (used for ventilation estimates).

    Examples
    --------
    >>> calc = HeatingLoadCalculator(
    ...     climate_zone=ClimateZone.MODERATE_COLD,
    ...     building_type="residential",
    ...     heated_area_m2=450,
    ... )
    >>> envelope = EnvelopeSpec(
    ...     wall_area_m2=300, roof_area_m2=150,
    ...     floor_area_m2=150, window_area_m2=60,
    ... )
    >>> result = calc.calculate(envelope)
    >>> print(f"Heating load: {result.total_heating_load_kw:.1f} kW")
    """

    def __init__(
        self,
        climate_zone: ClimateZone,
        building_type: str = "residential",
        heated_area_m2: float = 100.0,
    ) -> None:
        self.climate_zone = climate_zone
        self.building_type = building_type.lower()
        self.heated_area_m2 = heated_area_m2

    def calculate(
        self,
        envelope: EnvelopeSpec,
        *,
        ventilation_rate_ach: float = 0.5,
        room_height_m: float = 2.7,
        safety_factor: float = 1.15,
    ) -> LoadResult:
        """Calculate the design heating load.

        Parameters
        ----------
        envelope : EnvelopeSpec
            Building envelope properties.
        ventilation_rate_ach : float
            Air changes per hour (default 0.5).
        room_height_m : float
            Average room height in metres.
        safety_factor : float
            Multiplicative safety margin (default 15 %).

        Returns
        -------
        LoadResult
        """
        t_indoor = SETPOINT_TEMP.get(self.building_type, 20.0)
        t_outdoor = self.climate_zone.design_outdoor_temp
        delta_t = t_indoor - t_outdoor

        # --- Transmission losses ---
        q_wall = envelope.wall_area_m2 * envelope.u_wall * delta_t
        q_roof = envelope.roof_area_m2 * envelope.u_roof * delta_t
        q_floor = envelope.floor_area_m2 * envelope.u_floor * delta_t * 0.6  # ground factor
        q_window = envelope.window_area_m2 * envelope.u_window * delta_t
        transmission = q_wall + q_roof + q_floor + q_window

        # --- Ventilation losses ---
        volume = self.heated_area_m2 * room_height_m
        air_flow_m3_s = volume * ventilation_rate_ach / 3600.0
        rho_cp = 1200.0  # ρ·c_p for air ≈ 1.2 kg/m³ · 1000 J/(kg·K)
        ventilation = air_flow_m3_s * rho_cp * delta_t

        # --- Total ---
        total = (transmission + ventilation) * safety_factor

        assumptions = [
            f"Indoor set-point: {t_indoor} °C",
            f"Outdoor design temp: {t_outdoor} °C (zone: {self.climate_zone.value})",
            f"Air change rate: {ventilation_rate_ach} ACH",
            f"Room height: {room_height_m} m",
            f"Safety factor: {safety_factor}",
            "Ground-contact floor loss reduced by factor 0.6",
            "No thermal bridge surcharge applied",
        ]

        logger.info(
            "Load calculation complete: %.1f kW (%.0f W/m²)",
            total / 1000,
            total / self.heated_area_m2,
        )

        return LoadResult(
            transmission_loss_w=round(transmission, 1),
            ventilation_loss_w=round(ventilation, 1),
            total_heating_load_w=round(total, 1),
            specific_load_w_per_m2=round(total / self.heated_area_m2, 1),
            assumptions=assumptions,
        )
