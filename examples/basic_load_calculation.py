#!/usr/bin/env python3
"""Example: basic heating-load calculation."""

from ai_hvac.hvac.load_calc import ClimateZone, EnvelopeSpec, HeatingLoadCalculator

envelope = EnvelopeSpec(
    wall_area_m2=320,
    roof_area_m2=160,
    floor_area_m2=160,
    window_area_m2=70,
    u_wall=0.28,
    u_roof=0.20,
    u_floor=0.35,
    u_window=1.30,
)

calc = HeatingLoadCalculator(
    climate_zone=ClimateZone.MODERATE_COLD,
    building_type="residential",
    heated_area_m2=480,
)

result = calc.calculate(
    envelope,
    ventilation_rate_ach=0.5,
    room_height_m=2.7,
    safety_factor=1.15,
)

print("=" * 60)
print("HEATING LOAD CALCULATION RESULT")
print("=" * 60)
print(f"  Transmission losses : {result.transmission_loss_w:,.0f} W")
print(f"  Ventilation losses  : {result.ventilation_loss_w:,.0f} W")
print(f"  Total heating load  : {result.total_heating_load_kw:.1f} kW")
print(f"  Specific load       : {result.specific_load_w_per_m2:.0f} W/m2")
print()
print("Assumptions:")
for assumption in result.assumptions:
    print(f"  - {assumption}")
