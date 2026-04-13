"""
Unit conversion utilities for HVAC engineering.

All conversions are implemented as pure functions (no side effects) and
as methods on the :class:`UnitConverter` convenience class.
"""

from __future__ import annotations


class UnitConverter:
    """Collection of static unit-conversion methods for HVAC quantities."""

    # -- Temperature --------------------------------------------------------

    @staticmethod
    def celsius_to_kelvin(t_c: float) -> float:
        """Convert Celsius to Kelvin."""
        return t_c + 273.15

    @staticmethod
    def kelvin_to_celsius(t_k: float) -> float:
        """Convert Kelvin to Celsius."""
        return t_k - 273.15

    @staticmethod
    def fahrenheit_to_celsius(t_f: float) -> float:
        """Convert Fahrenheit to Celsius."""
        return (t_f - 32.0) * 5.0 / 9.0

    @staticmethod
    def celsius_to_fahrenheit(t_c: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return t_c * 9.0 / 5.0 + 32.0

    # -- Energy / Power -----------------------------------------------------

    @staticmethod
    def kw_to_btu_h(kw: float) -> float:
        """Convert kilowatts to BTU/h."""
        return kw * 3412.14

    @staticmethod
    def btu_h_to_kw(btu_h: float) -> float:
        """Convert BTU/h to kilowatts."""
        return btu_h / 3412.14

    @staticmethod
    def kwh_to_mj(kwh: float) -> float:
        """Convert kWh to MJ."""
        return kwh * 3.6

    @staticmethod
    def mj_to_kwh(mj: float) -> float:
        """Convert MJ to kWh."""
        return mj / 3.6

    @staticmethod
    def kwh_to_therm(kwh: float) -> float:
        """Convert kWh to therms."""
        return kwh * 0.034121

    # -- Pressure -----------------------------------------------------------

    @staticmethod
    def bar_to_pa(bar: float) -> float:
        """Convert bar to Pascal."""
        return bar * 100_000.0

    @staticmethod
    def pa_to_bar(pa: float) -> float:
        """Convert Pascal to bar."""
        return pa / 100_000.0

    @staticmethod
    def psi_to_bar(psi: float) -> float:
        """Convert PSI to bar."""
        return psi * 0.0689476

    # -- Flow ---------------------------------------------------------------

    @staticmethod
    def m3h_to_ls(m3h: float) -> float:
        """Convert m³/h to litres/s."""
        return m3h / 3.6

    @staticmethod
    def ls_to_m3h(ls: float) -> float:
        """Convert litres/s to m³/h."""
        return ls * 3.6

    @staticmethod
    def gpm_to_ls(gpm: float) -> float:
        """Convert US gallons per minute to litres/s."""
        return gpm * 0.063090

    # -- Area / Length (Imperial ↔ Metric) -----------------------------------

    @staticmethod
    def sqft_to_m2(sqft: float) -> float:
        """Convert square feet to m²."""
        return sqft * 0.092903

    @staticmethod
    def m2_to_sqft(m2: float) -> float:
        """Convert m² to square feet."""
        return m2 / 0.092903

    # -- U-value conversions ------------------------------------------------

    @staticmethod
    def r_value_to_u_value(r_imperial: float) -> float:
        """Convert imperial R-value (ft²·°F·h/BTU) to U-value (W/m²K)."""
        return 5.678 / r_imperial if r_imperial > 0 else 0.0

    @staticmethod
    def u_value_to_r_value(u_si: float) -> float:
        """Convert U-value (W/m²K) to imperial R-value."""
        return 5.678 / u_si if u_si > 0 else 0.0
