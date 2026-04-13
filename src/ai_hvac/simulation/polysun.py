"""Polysun simulation template generator."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class HeatGenerator:
    """Heat generator specification."""

    type: str = "Air-source heat pump"
    nominal_power_kw: float = 10.0
    cop_nominal: float = 3.5
    supply_temp_c: float = 45.0


@dataclass
class StorageTank:
    """Thermal storage tank specification."""

    purpose: str = "buffer"
    volume_litres: float = 500.0
    insulation_mm: float = 100.0
    setpoint_temp_c: float = 50.0


@dataclass
class SolarThermal:
    """Solar thermal or PVT collector specification."""

    type: str = "flat_plate"
    area_m2: float = 10.0
    orientation: str = "south"
    tilt_deg: float = 35.0
    eta_0: float = 0.80


@dataclass
class PolysunTemplate:
    """Complete Polysun simulation template."""

    name: str = ""
    heat_generator: HeatGenerator = field(default_factory=HeatGenerator)
    backup_generator: HeatGenerator | None = None
    buffer_tank: StorageTank = field(default_factory=StorageTank)
    dhw_tank: StorageTank | None = None
    solar: SolarThermal | None = None
    control_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict."""
        return asdict(self)

    def to_json(self, indent: int = 2, *, ensure_ascii: bool = True) -> str:
        """Serialise to a formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)


class PolysunTemplateGenerator:
    """Generate Polysun simulation templates from design parameters."""

    def __init__(
        self,
        heating_load_kw: float,
        building_type: str = "residential",
        dhw_demand_litres_day: float = 200.0,
    ) -> None:
        self.heating_load_kw: float = heating_load_kw
        self.building_type: str = building_type
        self.dhw_demand: float = dhw_demand_litres_day

    def heat_pump_template(
        self,
        *,
        hp_type: str = "air_source",
        with_solar: bool = False,
    ) -> PolysunTemplate:
        """Generate a heat-pump-based Polysun template."""
        hp_label = "Air-source heat pump" if hp_type == "air_source" else "Ground-source heat pump"
        cop = 3.5 if hp_type == "air_source" else 4.5
        hp_power = round(self.heating_load_kw * 1.1, 1)

        template = PolysunTemplate(
            name=f"{hp_label} - {self.building_type}",
            heat_generator=HeatGenerator(
                type=hp_label,
                nominal_power_kw=hp_power,
                cop_nominal=cop,
                supply_temp_c=45.0,
            ),
            buffer_tank=StorageTank(
                purpose="buffer",
                volume_litres=max(300, hp_power * 30),
                setpoint_temp_c=45.0,
            ),
            dhw_tank=StorageTank(
                purpose="dhw",
                volume_litres=max(200, self.dhw_demand * 1.5),
                setpoint_temp_c=55.0,
            ),
            control_notes=[
                "Set heat pump as priority heat source (Controller 1).",
                "Buffer tank hysteresis: ON at 38 degC, OFF at 45 degC.",
                "DHW priority: enable DHW boost via 3-way valve when T_dhw < 50 degC.",
                "Ensure anti-legionella cycle >= 60 degC once per week.",
            ],
        )

        if with_solar:
            solar_area = round(self.heating_load_kw * 1.5, 1)
            template.solar = SolarThermal(
                type="pvt" if hp_type == "ground_source" else "flat_plate",
                area_m2=solar_area,
                tilt_deg=35.0,
            )
            template.control_notes.append(
                "Solar loop feeds buffer tank bottom; use delta-T controller (ON: delta-T > 8 K)."
            )

        logger.info("Generated Polysun template: %s", template.name)
        return template

    def gas_boiler_template(self) -> PolysunTemplate:
        """Generate a condensing gas boiler Polysun template."""
        boiler_power = round(self.heating_load_kw * 1.15, 1)
        return PolysunTemplate(
            name=f"Condensing gas boiler - {self.building_type}",
            heat_generator=HeatGenerator(
                type="Gas condensing boiler",
                nominal_power_kw=boiler_power,
                cop_nominal=0.96,
                supply_temp_c=70.0,
            ),
            buffer_tank=StorageTank(
                purpose="buffer",
                volume_litres=max(200, boiler_power * 20),
                setpoint_temp_c=65.0,
            ),
            dhw_tank=StorageTank(
                purpose="dhw",
                volume_litres=max(200, self.dhw_demand * 1.5),
                setpoint_temp_c=60.0,
            ),
            control_notes=[
                "Outdoor-temperature-compensated supply temperature curve.",
                "Heating curve: 20/70 -> 20/30 (slope and offset adjustable).",
                "DHW priority via 3-way valve.",
            ],
        )

    def hybrid_template(self) -> PolysunTemplate:
        """Generate a heat pump and gas boiler hybrid template."""
        hp_power = round(self.heating_load_kw * 0.7, 1)
        boiler_power = round(self.heating_load_kw * 0.5, 1)
        return PolysunTemplate(
            name=f"Hybrid HP + Gas - {self.building_type}",
            heat_generator=HeatGenerator(
                type="Air-source heat pump",
                nominal_power_kw=hp_power,
                cop_nominal=3.2,
                supply_temp_c=45.0,
            ),
            backup_generator=HeatGenerator(
                type="Gas condensing boiler (backup)",
                nominal_power_kw=boiler_power,
                cop_nominal=0.96,
                supply_temp_c=70.0,
            ),
            buffer_tank=StorageTank(
                purpose="buffer",
                volume_litres=max(500, hp_power * 40),
                setpoint_temp_c=45.0,
            ),
            dhw_tank=StorageTank(
                purpose="dhw",
                volume_litres=max(200, self.dhw_demand * 1.5),
                setpoint_temp_c=55.0,
            ),
            control_notes=[
                "Bivalent-parallel operation: HP runs as base, boiler kicks in below -2 degC.",
                "HP controller: priority heat source, buffer hysteresis 38-45 degC.",
                "Boiler controller: enable when buffer T < 35 degC and outdoor T < -2 degC.",
                "DHW: heat pump charges DHW tank to 55 degC; boiler boost to 60 degC if needed.",
            ],
        )
