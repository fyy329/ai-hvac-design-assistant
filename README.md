# AI HVAC Design Assistant

AI-powered toolkit for HVAC system design, load calculation, and simulation automation.

[![CI](https://github.com/fyy329/ai-hvac-design-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/fyy329/ai-hvac-design-assistant/actions/workflows/ci.yml)
[![Lint](https://github.com/fyy329/ai-hvac-design-assistant/actions/workflows/lint.yml/badge.svg)](https://github.com/fyy329/ai-hvac-design-assistant/actions/workflows/lint.yml)
[![License](https://img.shields.io/github/license/fyy329/ai-hvac-design-assistant)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

## What It Does

The project focuses on common early-stage HVAC engineering workflows:

- deterministic heating-load calculations
- rule-based and AI-assisted system recommendations
- Polysun-oriented simulation templates
- Modelica skeleton generation
- unit conversions and input validation helpers

The goal is to make repetitive design and simulation setup work easier to automate without hiding engineering assumptions.

## Installation

```bash
git clone https://github.com/fyy329/ai-hvac-design-assistant.git
cd ai-hvac-design-assistant
python -m venv .venv
```

Activate the virtual environment:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the package with development tools:

```bash
pip install -e ".[dev]"
```

If you want to use AI-backed features, create a `.env` file and add your API key:

```bash
copy .env.example .env
```

Then set:

```env
OPENAI_API_KEY=sk-your-key-here
```

## Quick Start

### Python API

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

AI-assisted recommendation:

```python
from ai_hvac import HVACAssistant

assistant = HVACAssistant()
recommendation = assistant.recommend_system(
    building_type="multi-family residential",
    location="Munich, Germany",
    heated_area_m2=2400,
    additional_context="Underfloor heating, 35/28 degC design temps, rooftop PVT possible",
)

print(recommendation.system_type)
print(recommendation.estimated_cop)
for component in recommendation.components:
    print(f"  - {component}")
```

Polysun template generation:

```python
from ai_hvac.simulation.polysun import PolysunTemplateGenerator

generator = PolysunTemplateGenerator(heating_load_kw=25.0, dhw_demand_litres_day=400)
template = generator.heat_pump_template(hp_type="ground_source", with_solar=True)
print(template.to_json())
```

### CLI

The package exposes the `ai-hvac` command:

```bash
ai-hvac version
```

Heating-load calculation from the command line:

```bash
ai-hvac load-calc ^
  --heated-area-m2 480 ^
  --wall-area-m2 320 ^
  --roof-area-m2 160 ^
  --floor-area-m2 160 ^
  --window-area-m2 70
```

Polysun-oriented template output:

```bash
ai-hvac polysun-template --heating-load-kw 25 --with-solar
```

## Development

Run the core checks locally before pushing:

```bash
pytest
ruff check src tests examples
ruff format --check src tests examples
mypy src tests examples
basedpyright
```

Example scripts:

```bash
python examples/basic_load_calculation.py
python examples/polysun_template_generation.py
python examples/ai_system_recommendation.py
```

The AI example requires `OPENAI_API_KEY`.

## Project Structure

```text
src/ai_hvac/
|- core/        # configuration and exception types
|- hvac/        # load calculation, system design, reference data
|- llm/         # OpenAI client, prompts, parsing helpers
|- simulation/  # Polysun and Modelica template generation
`- utils/       # converters and validators
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Roadmap](ROADMAP.md)

## Supported Standards and Tools

| Standard / Tool | Coverage |
|-----------------|----------|
| DIN EN 12831 | Simplified heating-load calculation |
| DIN 4108 / EnEV / GEG | Reference U-value tables |
| DIN 4708 / VDI 2067 | DHW demand profiles |
| Polysun | Simulation template generation |
| Modelica / AixLib | Skeleton model generation |
| ASHRAE | Design-condition reference data |

## Contributing

Contributions are welcome. See [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md).

Areas that still have plenty of room for improvement:

- cooling-load calculation
- weather and climate file integration
- automated Polysun export formats
- HVAC standards retrieval / RAG
- web UI and visualization

## License

[MIT](LICENSE)
