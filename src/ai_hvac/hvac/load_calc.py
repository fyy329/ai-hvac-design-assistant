"""Simplified heating-load calculator."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

from ai_hvac.utils.validators import (
    validate_area,
    validate_non_negative,
    validate_positive,
    validate_u_value,
)

logger = logging.getLogger(__name__)


class ClimateZone(Enum):
    """Simplified climate zones based on outdoor design temperatures."""

    COLD = "cold"
    MODERATE_COLD = "moderate_cold"
    MODERATE = "moderate"
    MILD = "mild"

    @property
    def design_outdoor_temp(self) -> float:
        """Return the outdoor design temperature in degC."""
        return {
            ClimateZone.COLD: -20.0,
            ClimateZone.MODERATE_COLD: -12.0,
            ClimateZone.MODERATE: -5.0,
            ClimateZone.MILD: 0.0,
        }[self]


DEFAULT_U_VALUES: dict[str, dict[str, float]] = {
    "pre_1980": {"wall": 1.4, "roof": 0.9, "floor": 1.0, "window": 2.8},
    "1980_2000": {"wall": 0.6, "roof": 0.4, "floor": 0.5, "window": 1.8},
    "post_2000": {"wall": 0.28, "roof": 0.20, "floor": 0.35, "window": 1.3},
    "passive_house": {"wall": 0.15, "roof": 0.10, "floor": 0.15, "window": 0.80},
}

INTERNAL_GAINS: dict[str, float] = {
    "residential": 5.0,
    "office": 15.0,
    "school": 10.0,
    "retail": 12.0,
    "hospital": 18.0,
}

SETPOINT_TEMP: dict[str, float] = {
    "residential": 20.0,
    "office": 21.0,
    "school": 20.0,
    "hospital": 22.0,
}


@dataclass
class EnvelopeSpec:
    """Building envelope specification."""

    wall_area_m2: float
    roof_area_m2: float
    floor_area_m2: float
    window_area_m2: float
    u_wall: float = 0.28
    u_roof: float = 0.20
    u_floor: float = 0.35
    u_window: float = 1.3

    def __post_init__(self) -> None:
        self.wall_area_m2 = validate_area(self.wall_area_m2, name="wall_area_m2")
        self.roof_area_m2 = validate_area(self.roof_area_m2, name="roof_area_m2")
        self.floor_area_m2 = validate_area(self.floor_area_m2, name="floor_area_m2")
        self.window_area_m2 = validate_area(self.window_area_m2, name="window_area_m2")
        self.u_wall = validate_u_value(self.u_wall, name="u_wall")
        self.u_roof = validate_u_value(self.u_roof, name="u_roof")
        self.u_floor = validate_u_value(self.u_floor, name="u_floor")
        self.u_window = validate_u_value(self.u_window, name="u_window")


@dataclass
class LoadResult:
    """Result of a heating-load calculation."""

    transmission_loss_w: float = 0.0
    ventilation_loss_w: float = 0.0
    total_heating_load_w: float = 0.0
    specific_load_w_per_m2: float = 0.0
    assumptions: list[str] = field(default_factory=list)

    @property
    def total_heating_load_kw(self) -> float:
        """Total heating load in kW."""
        return self.total_heating_load_w / 1000.0


class HeatingLoadCalculator:
    """Simplified heating-load calculator."""

    def __init__(
        self,
        climate_zone: ClimateZone,
        building_type: str = "residential",
        heated_area_m2: float = 100.0,
    ) -> None:
        self.climate_zone: ClimateZone = climate_zone
        self.building_type: str = building_type.lower()
        self.heated_area_m2: float = validate_area(heated_area_m2, name="heated_area_m2")

    def calculate(
        self,
        envelope: EnvelopeSpec,
        *,
        ventilation_rate_ach: float = 0.5,
        room_height_m: float = 2.7,
        safety_factor: float = 1.15,
    ) -> LoadResult:
        """Calculate the design heating load."""
        ventilation_rate_ach = validate_non_negative(
            ventilation_rate_ach, name="ventilation_rate_ach"
        )
        room_height_m = validate_positive(room_height_m, name="room_height_m")
        safety_factor = validate_positive(safety_factor, name="safety_factor")

        t_indoor = SETPOINT_TEMP.get(self.building_type, 20.0)
        t_outdoor = self.climate_zone.design_outdoor_temp
        delta_t = t_indoor - t_outdoor

        q_wall = envelope.wall_area_m2 * envelope.u_wall * delta_t
        q_roof = envelope.roof_area_m2 * envelope.u_roof * delta_t
        q_floor = envelope.floor_area_m2 * envelope.u_floor * delta_t * 0.6
        q_window = envelope.window_area_m2 * envelope.u_window * delta_t
        transmission = q_wall + q_roof + q_floor + q_window

        volume = self.heated_area_m2 * room_height_m
        air_flow_m3_s = volume * ventilation_rate_ach / 3600.0
        rho_cp = 1200.0
        ventilation = air_flow_m3_s * rho_cp * delta_t

        total = (transmission + ventilation) * safety_factor

        assumptions = [
            f"Indoor set-point: {t_indoor} degC",
            f"Outdoor design temp: {t_outdoor} degC (zone: {self.climate_zone.value})",
            f"Air change rate: {ventilation_rate_ach} ACH",
            f"Room height: {room_height_m} m",
            f"Safety factor: {safety_factor}",
            "Ground-contact floor loss reduced by factor 0.6",
            "No thermal bridge surcharge applied",
        ]

        logger.info(
            "Load calculation complete: %.1f kW (%.0f W/m2)",
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
