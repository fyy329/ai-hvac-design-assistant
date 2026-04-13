<p align="center">
  <h1 align="center">🏗️ AI HVAC Design Assistant</h1>
  <p align="center">
    <strong>AI-powered toolkit for HVAC system design, load calculation, and building energy simulation automation.</strong>
  </p>
  <p align="center">
    <a href="https://github.com/fyy329/ai-hvac-design-assistant/actions/workflows/ci.yml"><img src="https://github.com/fyy329/ai-hvac-design-assistant/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
    <a href="https://github.com/fyy329/ai-hvac-design-assistant/actions/workflows/lint.yml"><img src="https://github.com/fyy329/ai-hvac-design-assistant/actions/workflows/lint.yml/badge.svg" alt="Lint"></a>
    <a href="https://github.com/fyy329/ai-hvac-design-assistant/blob/main/LICENSE"><img src="https://img.shields.io/github/license/fyy329/ai-hvac-design-assistant" alt="License"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+"></a>
  </p>
</p>

---

## 🎯 The Problem

HVAC and building energy system design involves **repetitive, complex workflows**: calculating heating loads, selecting equipment, configuring simulation software, comparing design variants. Engineers spend countless hours on tasks that follow predictable patterns — exactly the kind of work AI can accelerate.

Yet unlike software development (which has Copilot, Cursor, etc.), **the HVAC engineering domain has virtually no open-source AI tooling**.

## 💡 The Solution

**AI HVAC Design Assistant** bridges this gap by providing:

- 🔢 **Deterministic Calculators** — Heating load calculation based on DIN EN 12831, with standard reference data (U-values, design temperatures, DHW demand).
- 🤖 **AI-Powered Design** — OpenAI-backed system recommendations, load estimation, and interactive Q&A with HVAC-domain expertise.
- ⚙️ **Simulation Automation** — Generate pre-configured templates for [Polysun](https://www.velasolaris.com/) and [Modelica](https://modelica.org/) from design parameters.
- 🔄 **Unit Conversions** — Comprehensive metric ↔ imperial converters for temperatures, energy, pressure, flow rates, and U-values.

```
Building Parameters ──▶ Load Calculator ──▶ System Recommender ──▶ Simulation Template
        │                                         │
        └──── AI Enhancement (OpenAI) ────────────┘
```

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/fyy329/ai-hvac-design-assistant.git
cd ai-hvac-design-assistant
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -e ".[dev]"
```

### Heating Load Calculation (no API key needed)

```python
from ai_hvac.hvac.load_calc import ClimateZone, EnvelopeSpec, HeatingLoadCalculator

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

### AI System Recommendation (requires OpenAI API key)

```python
from ai_hvac import HVACAssistant

assistant = HVACAssistant()
rec = assistant.recommend_system(
    building_type="multi-family residential",
    location="Munich, Germany",
    heated_area_m2=2400,
    additional_context="Underfloor heating, 35/28 °C design temps, rooftop PVT possible",
)

print(f"System: {rec.system_type}")
print(f"COP: {rec.estimated_cop}")
for comp in rec.components:
    print(f"  • {comp}")
```

### Generate Polysun Template

```python
from ai_hvac.simulation.polysun import PolysunTemplateGenerator

gen = PolysunTemplateGenerator(heating_load_kw=25.0, dhw_demand_litres_day=400)
template = gen.heat_pump_template(hp_type="ground_source", with_solar=True)
print(template.to_json())
```

## 📦 Project Structure

```
src/ai_hvac/
├── core/          # Configuration, exceptions
├── llm/           # OpenAI client, prompts, parsers
├── hvac/          # Load calc, system design, standards data
├── simulation/    # Polysun & Modelica template generators
└── utils/         # Unit converters, validators
```

## 🧪 Running Tests

```bash
pytest
```

## 📋 Supported Standards & Tools

| Standard / Tool | Coverage |
|----------------|----------|
| DIN EN 12831 | Simplified heating load calculation |
| DIN 4108 / EnEV / GEG | U-value reference tables |
| DIN 4708 / VDI 2067 | DHW demand profiles |
| Polysun | Simulation template generation |
| Modelica / AixLib | Skeleton model generation |
| ASHRAE | Design condition data |

## 🗺️ Roadmap

See [ROADMAP.md](ROADMAP.md) for the full development plan. Key upcoming features:

- Cooling load calculator (VDI 2078)
- Weather data integration (TRY / TMY / EPW)
- Automated Polysun XML generation
- RAG pipeline for HVAC standards retrieval
- Web-based interactive demo
- BIM / IFC data import

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for guidelines.

**Areas where help is especially needed:**
- HVAC standards implementation (cooling loads, DHW profiles)
- Climate / weather data parsing
- Multi-language documentation (DE, ZH)
- Web UI development

## 📄 License

[MIT](LICENSE) — free for academic, commercial, and personal use.

## 🔗 Related Projects

- [Polysun](https://www.velasolaris.com/) — Solar and HVAC system simulation
- [nPro](https://npro.energy/) — District energy planning
- [AixLib](https://github.com/RWTH-EBC/AixLib) — Modelica library for building energy
- [TEASER](https://github.com/RWTH-EBC/TEASER) — Building model generator for Modelica
- [OpenModelica](https://openmodelica.org/) — Open-source Modelica simulation
