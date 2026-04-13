# Contributing to AI HVAC Design Assistant

Thank you for your interest in contributing! This project aims to build the leading open-source AI toolkit for HVAC and building energy system design.

## How to Contribute

### Reporting Bugs

- Use the [Bug Report](https://github.com/fyy329/ai-hvac-design-assistant/issues/new?template=bug_report.md) template
- Include Python version, OS, and full error traceback
- Provide a minimal reproducible example if possible

### Suggesting Features

- Use the [Feature Request](https://github.com/fyy329/ai-hvac-design-assistant/issues/new?template=feature_request.md) template
- Describe the use case and why it matters for HVAC engineers

### Submitting Code

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Install dev dependencies**: `pip install -e ".[dev]"`
4. **Write tests** for your changes
5. **Run the test suite**: `pytest`
6. **Run the linter**: `ruff check src/ tests/`
7. **Commit** with a descriptive message
8. **Push** and open a Pull Request

### Code Style

- We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- Target Python 3.10+
- Use type hints for all function signatures
- Write docstrings in NumPy style
- Keep functions focused and < 50 lines where possible

### Testing

- All new features should have corresponding tests in `tests/`
- Use `pytest` fixtures for shared test data
- Mock external API calls (never make real OpenAI calls in tests)
- Aim for meaningful test coverage, not just line coverage

## Development Setup

```bash
git clone https://github.com/fyy329/ai-hvac-design-assistant.git
cd ai-hvac-design-assistant
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Areas Where Help Is Needed

- 🔬 **HVAC standards implementation** — Cooling load (VDI 2078), DHW profiles (DIN 4708)
- 🌍 **Climate data** — Weather file parsing (TRY, TMY, EPW formats)
- 🏗️ **BIM integration** — IFC data import for building geometry
- 📚 **Documentation** — Tutorials, translations (DE, ZH)
- 🧪 **Testing** — Edge cases, integration tests
- 🎨 **Web UI** — Streamlit or Gradio interactive demo

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.
