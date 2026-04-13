#!/usr/bin/env python3
"""Example: AI-powered HVAC system recommendation."""

import os
import sys

if not os.getenv("OPENAI_API_KEY"):
    print("OPENAI_API_KEY not set. Copy .env.example to .env and add your key.")
    print("This example requires an active OpenAI API key.")
    sys.exit(1)

from ai_hvac import HVACAssistant

assistant = HVACAssistant()

print("Requesting AI system recommendation...")
print()

recommendation = assistant.recommend_system(
    building_type="multi-family residential",
    location="Munich, Germany",
    heated_area_m2=2400,
    cooling_required=False,
    dhw_required=True,
    additional_context=(
        "The building has 24 apartments across 4 floors. "
        "Underfloor heating with 35/28 degC design temperatures. "
        "Rooftop available for PVT collectors (~120 m2). "
        "Gas connection available as backup."
    ),
)

print("=" * 60)
print("AI SYSTEM RECOMMENDATION")
print("=" * 60)
print(f"  System type   : {recommendation.system_type}")
print(f"  Estimated COP : {recommendation.estimated_cop}")
print()
print("Components:")
for component in recommendation.components:
    print(f"  - {component}")
print()
print(f"Rationale: {recommendation.rationale}")
print()
if recommendation.warnings:
    print("Warnings:")
    for warning in recommendation.warnings:
        print(f"  - {warning}")

print()
print("-" * 60)
answer = assistant.ask(
    "What is the recommended buffer tank volume for a 2400 m2 "
    "multi-family building with underfloor heating and an air-source "
    "heat pump? Give the answer in litres and explain the sizing rule."
)
print("Follow-up Q&A:")
print(answer)
