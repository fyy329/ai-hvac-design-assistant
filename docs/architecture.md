# Architecture

## High-Level Overview

```
┌───────────────────────────────────────────────┐
│                User / CLI / API               │
└──────────────────┬────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │   ai_hvac (Python)  │
        └──────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌────────┐  ┌──────────┐  ┌────────────┐
│  hvac  │  │   llm    │  │ simulation │
│        │  │          │  │            │
│ • load │  │ • client │  │ • polysun  │
│   calc │  │ • prompts│  │ • modelica │
│ • sys  │  │ • parsers│  │            │
│  design│  │          │  │            │
│ • std  │  │          │  │            │
└────┬───┘  └────┬─────┘  └─────┬──────┘
     │           │              │
     └───────────┼──────────────┘
                 │
        ┌────────▼────────┐
        │      core       │
        │ • config        │
        │ • exceptions    │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │     utils       │
        │ • converters    │
        │ • validators    │
        └─────────────────┘
```

## Module Responsibilities

### `core`
- **config.py** — Pydantic-settings configuration, loads from `.env`
- **exceptions.py** — Exception hierarchy (`AIHVACError` base class)

### `llm`
- **client.py** — `HVACAssistant` wraps OpenAI chat completions with HVAC-domain system prompts. Returns structured dataclasses (`SystemRecommendation`, `LoadEstimate`).
- **prompts.py** — `PromptLibrary` provides parameterised prompt templates that instruct the LLM to reply in JSON.
- **parsers.py** — Robust JSON extraction from LLM output (handles markdown fences, embedded JSON, type coercion).

### `hvac`
- **load_calc.py** — `HeatingLoadCalculator` implements DIN EN 12831 (simplified). Deterministic, no LLM dependency.
- **system_design.py** — `SystemDesigner` ranks HVAC system options using rule-based scoring (climate, load density, building type).
- **standards.py** — Reference data: design outdoor temps, U-value tables, DHW demand norms, degree-day methods.

### `simulation`
- **polysun.py** — `PolysunTemplateGenerator` outputs structured parameter sets for Polysun project setup (heat pump, boiler, hybrid, with/without solar).
- **modelica.py** — Generates skeleton Modelica `.mo` files for downstream simulation in OpenModelica / Dymola.

### `utils`
- **converters.py** — `UnitConverter` with methods for temperature, energy, pressure, flow, area, and U-value conversions.
- **validators.py** — Input validation functions that raise `ValidationError` with descriptive messages.

## Data Flow

1. **User** provides building parameters (type, location, area, envelope).
2. **`HeatingLoadCalculator`** computes design heating load (deterministic).
3. **`SystemDesigner`** (rule-based) or **`HVACAssistant`** (AI-powered) recommends a system configuration.
4. **`PolysunTemplateGenerator`** converts the recommendation into a simulation-ready parameter set.
5. **Engineer** uses the template to configure a Polysun or Modelica project.

## Technology Choices

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Language | Python 3.10+ | Dominant in scientific/engineering computing |
| LLM | OpenAI API | Best-in-class for structured JSON generation |
| Config | pydantic-settings | Type-safe, `.env` support, validation |
| Build | Hatch | Modern PEP 517 build system |
| Tests | pytest | Industry standard, excellent plugin ecosystem |
| Lint | Ruff | Fast, comprehensive Python linter |
