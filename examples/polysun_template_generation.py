#!/usr/bin/env python3
"""
Example: Polysun simulation template generation.

Generates a configured template for a heat-pump-based system and
prints it as JSON.  The output can guide manual setup in the Polysun
GUI or be used by future automation scripts.
"""

import json

from ai_hvac.hvac.load_calc import (
    ClimateZone,
    EnvelopeSpec,
    HeatingLoadCalculator,
)
from ai_hvac.simulation.polysun import PolysunTemplateGenerator

# 1. Calculate the heating load first
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

# 2. Generate Polysun templates for different system variants
gen = PolysunTemplateGenerator(
    heating_load_kw=load.total_heating_load_kw,
    building_type="residential",
    dhw_demand_litres_day=1200,  # ~24 apartments × 50 L/person
)

# Variant A: Heat pump only
print("=" * 60)
print("VARIANT A: Air-source heat pump")
print("=" * 60)
template_a = gen.heat_pump_template(hp_type="air_source", with_solar=False)
print(template_a.to_json())
print()

# Variant B: Heat pump + PVT
print("=" * 60)
print("VARIANT B: Ground-source HP + PVT")
print("=" * 60)
template_b = gen.heat_pump_template(hp_type="ground_source", with_solar=True)
print(template_b.to_json())
print()

# Variant C: Hybrid (HP + gas boiler)
print("=" * 60)
print("VARIANT C: Hybrid HP + Gas Boiler")
print("=" * 60)
template_c = gen.hybrid_template()
print(template_c.to_json())
print()

# Print control notes for Variant B
print("=" * 60)
print("POLYSUN GUI SETUP NOTES (Variant B)")
print("=" * 60)
for i, note in enumerate(template_b.control_notes, 1):
    print(f"  {i}. {note}")
