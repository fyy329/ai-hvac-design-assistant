# Getting Started

## Prerequisites

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Git** — [Download](https://git-scm.com/)
- **OpenAI API key** — Required only for AI-powered features. [Get one here](https://platform.openai.com/api-keys).

## Installation

### From source (recommended during early development)

```bash
# Clone the repository
git clone https://github.com/fyy329/ai-hvac-design-assistant.git
cd ai-hvac-design-assistant

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Configure environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

## Quick Start

### 1. Heating Load Calculation (no API key needed)

```python
from ai_hvac.hvac.load_calc import (
    ClimateZone, EnvelopeSpec, HeatingLoadCalculator,
)

calc = HeatingLoadCalculator(
    climate_zone=ClimateZone.MODERATE_COLD,
    building_type="residential",
    heated_area_m2=450,
)

envelope = EnvelopeSpec(
    wall_area_m2=300, roof_area_m2=150,
    floor_area_m2=150, window_area_m2=60,
)

result = calc.calculate(envelope)
print(f"Heating load: {result.total_heating_load_kw:.1f} kW")
print(f"Specific load: {result.specific_load_w_per_m2:.0f} W/m²")
```

### 2. AI System Recommendation (requires API key)

```python
from ai_hvac import HVACAssistant

assistant = HVACAssistant()
rec = assistant.recommend_system(
    building_type="office",
    location="Berlin, Germany",
    heated_area_m2=800,
)

print(f"Recommended: {rec.system_type}")
print(f"COP: {rec.estimated_cop}")
for comp in rec.components:
    print(f"  • {comp}")
```

### 3. Generate Polysun Template

```python
from ai_hvac.simulation.polysun import PolysunTemplateGenerator

gen = PolysunTemplateGenerator(
    heating_load_kw=25.0,
    building_type="residential",
    dhw_demand_litres_day=400,
)

template = gen.heat_pump_template(hp_type="air_source", with_solar=True)
print(template.to_json())
```

## Running Tests

```bash
pytest
```

## Running Examples

```bash
python examples/basic_load_calculation.py
python examples/polysun_template_generation.py

# Requires OPENAI_API_KEY:
python examples/ai_system_recommendation.py
```

## Next Steps

- Read the [Architecture Guide](architecture.md) to understand the codebase
- Check the [API Reference](api-reference.md) for detailed method docs
- See the [Roadmap](../ROADMAP.md) for planned features
