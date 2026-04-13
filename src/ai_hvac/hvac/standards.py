"""
Reference data from HVAC and building energy standards.

This module collects commonly needed constants and lookup tables from
DIN, EN, and ASHRAE standards so that calculators and LLM prompts can
reference authoritative values.
"""

from __future__ import annotations

from typing import NamedTuple

# ---------------------------------------------------------------------------
# DIN EN 12831 — Design outdoor temperatures for selected cities
# ---------------------------------------------------------------------------

class DesignCondition(NamedTuple):
    """Outdoor design conditions for a city."""

    city: str
    country: str
    heating_design_temp_c: float
    cooling_design_temp_c: float | None
    hdd_base18: int  # Heating degree days (base 18 °C)


DESIGN_CONDITIONS: list[DesignCondition] = [
    DesignCondition("Munich", "DE", -16.0, 32.0, 3600),
    DesignCondition("Berlin", "DE", -14.0, 31.0, 3200),
    DesignCondition("Hamburg", "DE", -12.0, 29.0, 3400),
    DesignCondition("Frankfurt", "DE", -12.0, 33.0, 3000),
    DesignCondition("Stuttgart", "DE", -14.0, 32.0, 3200),
    DesignCondition("Vienna", "AT", -14.0, 33.0, 3300),
    DesignCondition("Zurich", "CH", -14.0, 31.0, 3500),
    DesignCondition("Paris", "FR", -7.0, 33.0, 2500),
    DesignCondition("London", "GB", -4.0, 30.0, 2200),
    DesignCondition("Milan", "IT", -8.0, 34.0, 2400),
    DesignCondition("Stockholm", "SE", -18.0, 27.0, 4200),
    DesignCondition("Helsinki", "FI", -26.0, 26.0, 4800),
    DesignCondition("Madrid", "ES", -4.0, 38.0, 1800),
    DesignCondition("New York", "US", -15.0, 34.0, 2700),
    DesignCondition("Chicago", "US", -21.0, 34.0, 3600),
]


def get_design_condition(city: str) -> DesignCondition | None:
    """Look up design conditions by city name (case-insensitive)."""
    city_lower = city.lower()
    for dc in DESIGN_CONDITIONS:
        if dc.city.lower() == city_lower:
            return dc
    return None


# ---------------------------------------------------------------------------
# DIN 4108 / EnEV — Reference U-values (W/m²K) by building standard
# ---------------------------------------------------------------------------

REFERENCE_U_VALUES: dict[str, dict[str, float]] = {
    "EnEV_2014": {
        "wall": 0.28,
        "roof": 0.20,
        "floor": 0.35,
        "window": 1.30,
        "door": 1.80,
    },
    "GEG_2020": {
        "wall": 0.28,
        "roof": 0.20,
        "floor": 0.35,
        "window": 1.30,
        "door": 1.80,
    },
    "KfW_55": {
        "wall": 0.20,
        "roof": 0.14,
        "floor": 0.25,
        "window": 0.95,
        "door": 1.30,
    },
    "Passive_House": {
        "wall": 0.15,
        "roof": 0.10,
        "floor": 0.15,
        "window": 0.80,
        "door": 0.80,
    },
}


# ---------------------------------------------------------------------------
# DHW demand (DIN 4708 / VDI 2067)
# ---------------------------------------------------------------------------

#: Typical daily DHW demand per person in litres (at 60 °C).
DHW_DEMAND_LITRES_PER_PERSON: dict[str, float] = {
    "residential_low": 30.0,
    "residential_medium": 40.0,
    "residential_high": 50.0,
    "office": 10.0,
    "school": 5.0,
    "hospital": 80.0,
    "hotel": 60.0,
}


# ---------------------------------------------------------------------------
# Degree-day methods — rough annual energy estimate
# ---------------------------------------------------------------------------

def estimate_annual_heating_kwh(
    peak_load_kw: float,
    hdd: int,
    design_delta_t: float,
) -> float:
    """Rough annual heating energy estimate using degree-day method.

    Parameters
    ----------
    peak_load_kw : float
        Design peak heating load in kW.
    hdd : int
        Heating degree days (base 18 °C).
    design_delta_t : float
        Design temperature difference (indoor − outdoor) in K.

    Returns
    -------
    float
        Estimated annual heating demand in kWh.
    """
    if design_delta_t <= 0:
        return 0.0
    return peak_load_kw * hdd * 24 / design_delta_t
