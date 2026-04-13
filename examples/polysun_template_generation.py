#!/usr/bin/env python3
"""Example: Polysun simulation template generation."""

from ai_hvac.hvac.load_calc import ClimateZone, EnvelopeSpec, HeatingLoadCalculator
from ai_hvac.simulation.polysun import PolysunTemplateGenerator

envelope = EnvelopeSpec(
    wall_area_m2=600,
    roof_area_m2=250,
    floor_area_m2=250,
    window_area_m2=120,
    u_wall=0.28,
    u_roof=0.20,
    u_floor=0.35,
    u_window=1.30,
)

calc = HeatingLoadCalculator(
    climate_zone=ClimateZone.MODERATE_COLD,
    building_type="residential",
    heated_area_m2=1200,
)
load = calc.calculate(envelope)

print(f"Design heating load: {load.total_heating_load_kw:.1f} kW")
print()

generator = PolysunTemplateGenerator(
    heating_load_kw=load.total_heating_load_kw,
    building_type="residential",
    dhw_demand_litres_day=1200,
)

print("=" * 60)
print("VARIANT A: Air-source heat pump")
print("=" * 60)
template_a = generator.heat_pump_template(hp_type="air_source", with_solar=False)
print(template_a.to_json())
print()

print("=" * 60)
print("VARIANT B: Ground-source HP + PVT")
print("=" * 60)
template_b = generator.heat_pump_template(hp_type="ground_source", with_solar=True)
print(template_b.to_json())
print()

print("=" * 60)
print("VARIANT C: Hybrid HP + Gas Boiler")
print("=" * 60)
template_c = generator.hybrid_template()
print(template_c.to_json())
print()

print("=" * 60)
print("POLYSUN GUI SETUP NOTES (Variant B)")
print("=" * 60)
for index, note in enumerate(template_b.control_notes, start=1):
    print(f"  {index}. {note}")
