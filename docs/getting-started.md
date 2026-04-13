# Getting Started

## Prerequisites

- Python 3.10 or newer
- Git
- OpenAI API key for AI-backed features only

## Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/fyy329/ai-hvac-design-assistant.git
cd ai-hvac-design-assistant
python -m venv .venv
```

Activate the environment:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the project in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

## Configure Environment

Create a local `.env` file from the example:

```bash
copy .env.example .env
```

Add your API key if you plan to use AI features:

```env
OPENAI_API_KEY=sk-your-key-here
```

## Quick Start with Python

### 1. Heating-load calculation

```python
from ai_hvac.hvac.load_calc import ClimateZone, EnvelopeSpec, HeatingLoadCalculator

calc = HeatingLoadCalculator(
    climate_zone=ClimateZone.MODERATE_COLD,
    building_type="residential",
    heated_area_m2=450,
)

envelope = EnvelopeSpec(
    wall_area_m2=300,
    roof_area_m2=150,
    floor_area_m2=150,
    window_area_m2=60,
)

result = calc.calculate(envelope)
print(f"Heating load: {result.total_heating_load_kw:.1f} kW")
print(f"Specific load: {result.specific_load_w_per_m2:.0f} W/m2")
```

### 2. AI system recommendation

```python
from ai_hvac import HVACAssistant

assistant = HVACAssistant()
recommendation = assistant.recommend_system(
    building_type="office",
    location="Berlin, Germany",
    heated_area_m2=800,
)

print(f"Recommended: {recommendation.system_type}")
print(f"COP: {recommendation.estimated_cop}")
for component in recommendation.components:
    print(f"  - {component}")
```

### 3. Generate a Polysun template

```python
from ai_hvac.simulation.polysun import PolysunTemplateGenerator

generator = PolysunTemplateGenerator(
    heating_load_kw=25.0,
    building_type="residential",
    dhw_demand_litres_day=400,
)

template = generator.heat_pump_template(hp_type="air_source", with_solar=True)
print(template.to_json())
```

## Quick Start with the CLI

Show the installed version:

```bash
ai-hvac version
```

Run a heating-load calculation:

```bash
ai-hvac load-calc ^
  --heated-area-m2 480 ^
  --wall-area-m2 320 ^
  --roof-area-m2 160 ^
  --floor-area-m2 160 ^
  --window-area-m2 70
```

Generate a template for Polysun-style setup:

```bash
ai-hvac polysun-template --heating-load-kw 25 --with-solar
```

## Development Commands

```bash
pytest
ruff check src tests examples
ruff format --check src tests examples
mypy src tests examples
basedpyright
```

## Examples

```bash
python examples/basic_load_calculation.py
python examples/polysun_template_generation.py
python examples/ai_system_recommendation.py
```

## Next Steps

- Read the [Architecture Guide](architecture.md)
- Review the [API Reference](api-reference.md)
- Check the [Roadmap](../ROADMAP.md)
