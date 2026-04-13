# Architecture

## High-Level Overview

```text
User / CLI / Python API
          |
          v
     ai_hvac package
          |
    +-----+------+------------------+
    |            |                  |
    v            v                  v
  hvac          llm            simulation
    |            |                  |
    v            v                  v
load calc   OpenAI client     Polysun / Modelica
system design prompts         template generation
standards     parsers
          |
          v
        core
   config / exceptions
          |
          v
        utils
 converters / validators
```

## Module Responsibilities

### core

- `config.py`: pydantic-settings based configuration
- `exceptions.py`: shared exception hierarchy

### hvac

- `load_calc.py`: deterministic simplified heating-load calculation
- `system_design.py`: rule-based recommendation logic
- `standards.py`: climate, U-value, and DHW reference data

### llm

- `client.py`: high-level OpenAI wrapper for HVAC tasks
- `prompts.py`: prompt templates for structured outputs
- `parsers.py`: JSON extraction and response normalization

### simulation

- `polysun.py`: structured Polysun-style templates
- `modelica.py`: Modelica skeleton generation

### utils

- `converters.py`: engineering unit conversion helpers
- `validators.py`: reusable input validation functions

## Typical Data Flow

1. A user provides building parameters through Python or the CLI.
2. `HeatingLoadCalculator` estimates the heating load.
3. `SystemDesigner` or `HVACAssistant` proposes a system concept.
4. `PolysunTemplateGenerator` converts that concept into a simulation-oriented template.
5. The engineer reviews the assumptions and applies the output in a downstream workflow.

## Quality Gates

The repository uses several complementary checks:

- `pytest` for behavioural regression coverage
- `ruff check` for linting
- `ruff format --check` for formatting consistency
- `mypy` for static typing
- `basedpyright` for language-server-grade type validation against the `src/` layout
