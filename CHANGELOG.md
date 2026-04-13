# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-04-13

### Added

- **Core framework**: Configuration management via pydantic-settings, custom exception hierarchy.
- **Heating load calculator**: Simplified DIN EN 12831 implementation with climate zones, envelope specification, and structured results.
- **OpenAI integration**: `HVACAssistant` client with structured JSON output for system recommendations and load estimation.
- **Prompt library**: Domain-specific prompt templates for HVAC system design, load estimation, and Polysun configuration.
- **LLM output parsers**: Robust JSON extraction handling markdown fences and embedded objects.
- **System designer**: Rule-based HVAC system recommender with scoring heuristics for 6 system types.
- **Polysun templates**: Generator for heat pump, gas boiler, and hybrid system simulation parameter sets.
- **Modelica templates**: Skeleton model generator for heat pump and district heating systems.
- **Unit converters**: Temperature, energy, pressure, flow, area, and U-value conversions (metric ↔ imperial).
- **Input validators**: Domain-aware validation for temperatures, areas, U-values.
- **Standards reference data**: DIN EN 12831 design conditions, EnEV/GEG U-value tables, DHW demand norms.
- **Examples**: Basic load calculation, AI system recommendation, Polysun template generation.
- **Tests**: Unit tests for load calculator, LLM parsers, and unit converters.
- **CI/CD**: GitHub Actions for testing and linting.
- **Documentation**: Architecture guide, getting started guide, API reference, roadmap.
