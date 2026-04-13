# API Reference

> **Note:** This is a summary reference. For full docstrings, see the source code or run `help()` on any class/function in Python.

---

## `ai_hvac.hvac.load_calc`

### `HeatingLoadCalculator`

```python
HeatingLoadCalculator(
    climate_zone: ClimateZone,
    building_type: str = "residential",
    heated_area_m2: float = 100.0,
)
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `calculate()` | `envelope: EnvelopeSpec`, `ventilation_rate_ach=0.5`, `room_height_m=2.7`, `safety_factor=1.15` | `LoadResult` | Compute design heating load |

### `EnvelopeSpec`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `wall_area_m2` | `float` | — | External wall area (excl. windows) |
| `roof_area_m2` | `float` | — | Roof area |
| `floor_area_m2` | `float` | — | Ground-contact floor area |
| `window_area_m2` | `float` | — | Window / glazing area |
| `u_wall` | `float` | `0.28` | Wall U-value (W/m²K) |
| `u_roof` | `float` | `0.20` | Roof U-value |
| `u_floor` | `float` | `0.35` | Floor U-value |
| `u_window` | `float` | `1.30` | Window U-value |

### `LoadResult`

| Field | Type | Description |
|-------|------|-------------|
| `transmission_loss_w` | `float` | Envelope transmission losses (W) |
| `ventilation_loss_w` | `float` | Ventilation losses (W) |
| `total_heating_load_w` | `float` | Total peak heating load (W) |
| `specific_load_w_per_m2` | `float` | Load per m² heated area |
| `total_heating_load_kw` | `property` | Load in kW |
| `assumptions` | `list[str]` | Assumptions made |

---

## `ai_hvac.llm.client`

### `HVACAssistant`

```python
HVACAssistant(settings: Settings | None = None)
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `recommend_system(building_type, location, heated_area_m2, ...)` | `SystemRecommendation` | AI system recommendation |
| `estimate_loads(building_type, location, heated_area_m2, ...)` | `LoadEstimate` | AI-assisted load estimation |
| `ask(question)` | `str` | Free-form HVAC Q&A |

---

## `ai_hvac.hvac.system_design`

### `SystemDesigner`

```python
SystemDesigner(
    climate_zone: ClimateZone,
    building_type: str,
    load_result: LoadResult,
)
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `recommend(top_n=3)` | `list[DesignRecommendation]` | Ranked system recommendations (rule-based) |

---

## `ai_hvac.simulation.polysun`

### `PolysunTemplateGenerator`

```python
PolysunTemplateGenerator(
    heating_load_kw: float,
    building_type: str = "residential",
    dhw_demand_litres_day: float = 200.0,
)
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `heat_pump_template(hp_type, with_solar)` | `PolysunTemplate` | HP-based system template |
| `gas_boiler_template()` | `PolysunTemplate` | Gas boiler template |
| `hybrid_template()` | `PolysunTemplate` | HP + gas hybrid template |

---

## `ai_hvac.utils.converters`

### `UnitConverter`

All methods are `@staticmethod`. Key conversions:

| Method | Description |
|--------|-------------|
| `celsius_to_kelvin(t)` | °C → K |
| `fahrenheit_to_celsius(t)` | °F → °C |
| `kw_to_btu_h(kw)` | kW → BTU/h |
| `kwh_to_mj(kwh)` | kWh → MJ |
| `bar_to_pa(bar)` | bar → Pa |
| `r_value_to_u_value(r)` | R-value (imperial) → U-value (W/m²K) |
| `sqft_to_m2(sqft)` | ft² → m² |
| `m3h_to_ls(m3h)` | m³/h → L/s |
