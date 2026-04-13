# Roadmap

## Vision

Build the **leading open-source AI toolkit for HVAC and building energy system design**, empowering engineers worldwide to design faster, more accurately, and more sustainably.

---

## Phase 1 — Foundation (Current: v0.1.x) ✅

- [x] Project structure and packaging
- [x] Core configuration management (pydantic-settings)
- [x] Heating load calculator (DIN EN 12831 simplified)
- [x] OpenAI API client with structured JSON output
- [x] HVAC-domain prompt templates
- [x] Rule-based system recommender
- [x] Polysun simulation template generator
- [x] Modelica skeleton model generator
- [x] Unit converter utilities
- [x] Unit tests and CI pipeline

## Phase 2 — Enhanced Calculations (v0.2.x) 🔜

- [ ] Cooling load calculator (VDI 2078 / ASHRAE)
- [ ] DHW demand profiler (DIN 4708 / VDI 2067)
- [ ] Annual energy demand estimation (degree-day + bin method)
- [ ] Multi-zone load calculation support
- [ ] Weather data integration (TRY / TMY format parsing)

## Phase 3 — AI Enhancement (v0.3.x) 🧠

- [ ] Fine-tuned prompts for parametric design exploration
- [ ] AI-powered code review for simulation configs
- [ ] Automated Polysun XML generation (direct .pse file creation)
- [ ] LLM function-calling for interactive design sessions
- [ ] RAG pipeline for HVAC standards (DIN, EN, ASHRAE) retrieval
- [ ] Cost estimation integration (equipment + operating costs)

## Phase 4 — Simulation Integration (v0.4.x) ⚡

- [ ] Polysun CLI / API integration (when available)
- [ ] OpenModelica automated simulation runner
- [ ] Time-series result parsing and visualisation
- [ ] Automated variant comparison (heat pump vs gas vs hybrid)
- [ ] nPro energy planning data import/export

## Phase 5 — Community & Ecosystem (v0.5.x) 🌍

- [ ] Web-based interactive demo (Streamlit / Gradio)
- [ ] Plugin system for custom calculation modules
- [ ] Multi-language documentation (EN, DE, ZH)
- [ ] Community-contributed system templates
- [ ] Integration with BIM tools (IFC data import)
- [ ] Energy certificate pre-check (GEG / EnEV compliance)

## Phase 6 — Production Ready (v1.0.0) 🚀

- [ ] Comprehensive test coverage (>90%)
- [ ] Full API documentation with examples
- [ ] Performance benchmarking and optimisation
- [ ] Security audit and dependency scanning
- [ ] Stable public API with semantic versioning
- [ ] PyPI package publication

---

## Contributing

We welcome contributions at any phase! See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for guidelines.

Have an idea that's not on the roadmap? [Open a feature request](https://github.com/fyy329/ai-hvac-design-assistant/issues/new?template=feature_request.md).
