# API Reference

This is a concise reference for the main public surfaces of the project.

## ai_hvac.hvac.load_calc

### HeatingLoadCalculator

```python
HeatingLoadCalculator(
    climate_zone: ClimateZone,
    building_type: str = "residential",
    heated_area_m2: float = 100.0,
)
```

Methods:

| Method | Returns | Notes |
|--------|---------|-------|
| `calculate(envelope, ventilation_rate_ach=0.5, room_height_m=2.7, safety_factor=1.15)` | `LoadResult` | Deterministic design heating-load estimate |

### EnvelopeSpec

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `wall_area_m2` | `float` | required | External wall area excluding windows |
| `roof_area_m2` | `float` | required | Roof area |
| `floor_area_m2` | `float` | required | Ground-contact floor area |
| `window_area_m2` | `float` | required | Window or glazing area |
| `u_wall` | `float` | `0.28` | Wall U-value in W/(m2K) |
| `u_roof` | `float` | `0.20` | Roof U-value in W/(m2K) |
| `u_floor` | `float` | `0.35` | Floor U-value in W/(m2K) |
| `u_window` | `float` | `1.30` | Window U-value in W/(m2K) |

Validation:

- areas must be positive
- U-values must stay within plausible HVAC ranges

### LoadResult

| Field | Type | Description |
|-------|------|-------------|
| `transmission_loss_w` | `float` | Envelope transmission losses in W |
| `ventilation_loss_w` | `float` | Ventilation losses in W |
| `total_heating_load_w` | `float` | Peak heating load in W |
| `specific_load_w_per_m2` | `float` | Load per heated area in W/m2 |
| `assumptions` | `list[str]` | Human-readable assumptions |
| `total_heating_load_kw` | `property` | Convenience conversion to kW |

## ai_hvac.hvac.system_design

### SystemDesigner

```python
SystemDesigner(
    climate_zone: ClimateZone,
    building_type: str,
    load_result: LoadResult,
)
```

Methods:

| Method | Returns | Notes |
|--------|---------|-------|
| `recommend(top_n=3)` | `list[DesignRecommendation]` | Rule-based ranking that accounts for climate, load density, and building type |

### DesignRecommendation

| Field | Type | Description |
|-------|------|-------------|
| `rank` | `int` | 1 is best fit |
| `system_key` | `str` | Internal template key |
| `label` | `str` | Human-readable system label |
| `components` | `list[str]` | Major equipment items |
| `rationale` | `str` | Short engineering explanation |
| `estimated_cop` | `float | None` | COP or efficiency estimate |
| `warnings` | `list[str]` | Caveats to review |

## ai_hvac.llm.client

### HVACAssistant

```python
HVACAssistant(settings: Settings | None = None)
```

Methods:

| Method | Returns | Notes |
|--------|---------|-------|
| `recommend_system(building_type, location, heated_area_m2, ...)` | `SystemRecommendation` | AI-assisted system recommendation |
| `estimate_loads(building_type, location, heated_area_m2, ...)` | `LoadEstimate` | AI-assisted load estimation |
| `ask(question)` | `str` | Free-form HVAC Q&A |

### SystemRecommendation

| Field | Type |
|-------|------|
| `system_type` | `str` |
| `components` | `list[str]` |
| `estimated_cop` | `float | None` |
| `rationale` | `str` |
| `warnings` | `list[str]` |

### LoadEstimate

| Field | Type |
|-------|------|
| `heating_load_kw` | `float` |
| `cooling_load_kw` | `float | None` |
| `assumptions` | `list[str]` |
| `confidence` | `str` |

## ai_hvac.llm.parsers

Helpers for normalizing LLM responses:

| Function | Purpose |
|----------|---------|
| `extract_json(text)` | Extract JSON from plain text or fenced blocks |
| `safe_float(value, default=...)` | Coerce values to `float` safely |
| `safe_list(value)` | Normalize a value into `list[str]` |

## ai_hvac.simulation.polysun

### PolysunTemplateGenerator

```python
PolysunTemplateGenerator(
    heating_load_kw: float,
    building_type: str = "residential",
    dhw_demand_litres_day: float = 200.0,
)
```

Methods:

| Method | Returns |
|--------|---------|
| `heat_pump_template(hp_type="air_source", with_solar=False)` | `PolysunTemplate` |
| `gas_boiler_template()` | `PolysunTemplate` |
| `hybrid_template()` | `PolysunTemplate` |

### PolysunTemplate

Methods:

| Method | Returns | Notes |
|--------|---------|-------|
| `to_dict()` | `dict[str, object]` | Plain serializable structure |
| `to_json(indent=2, ensure_ascii=True)` | `str` | JSON output safe for terminals and files |

## ai_hvac.utils.converters

### UnitConverter

All methods are static methods.

Key conversions:

| Method | Description |
|--------|-------------|
| `celsius_to_kelvin(t)` | degC to K |
| `fahrenheit_to_celsius(t)` | degF to degC |
| `kw_to_btu_h(kw)` | kW to BTU/h |
| `kwh_to_mj(kwh)` | kWh to MJ |
| `bar_to_pa(bar)` | bar to Pa |
| `r_value_to_u_value(r)` | Imperial R-value to SI U-value |
| `sqft_to_m2(sqft)` | Square feet to m2 |
| `m3h_to_ls(m3h)` | m3/h to L/s |

## ai_hvac.cli

The installed command is `ai-hvac`.

Available commands:

| Command | Purpose |
|---------|---------|
| `ai-hvac version` | Show installed package version |
| `ai-hvac load-calc ...` | Run deterministic heating-load calculations |
| `ai-hvac polysun-template ...` | Emit a Polysun-oriented template as JSON |
| `ai-hvac recommend-system ...` | Request an AI-based recommendation |
