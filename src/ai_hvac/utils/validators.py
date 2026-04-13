"""
Input validation helpers.

These functions raise :class:`~ai_hvac.core.exceptions.ValidationError`
when constraints are violated, providing clear error messages.
"""

from __future__ import annotations

from ai_hvac.core.exceptions import ValidationError


def validate_positive(value: float, name: str = "value") -> float:
    """Ensure *value* is strictly positive.

    Parameters
    ----------
    value : float
        The value to check.
    name : str
        Human-readable parameter name for the error message.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    ValidationError
    """
    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")
    return value


def validate_non_negative(value: float, name: str = "value") -> float:
    """Ensure *value* is zero or positive.

    Raises
    ------
    ValidationError
    """
    if value < 0:
        raise ValidationError(f"{name} must be non-negative, got {value}")
    return value


def validate_temperature(
    temp_c: float,
    name: str = "temperature",
    *,
    min_c: float = -60.0,
    max_c: float = 200.0,
) -> float:
    """Ensure *temp_c* is within a plausible range for HVAC applications.

    Parameters
    ----------
    temp_c : float
        Temperature in °C.
    name : str
        Parameter name.
    min_c, max_c : float
        Allowed bounds.

    Returns
    -------
    float
        The validated temperature.

    Raises
    ------
    ValidationError
    """
    if not (min_c <= temp_c <= max_c):
        raise ValidationError(
            f"{name} = {temp_c} °C is outside plausible range [{min_c}, {max_c}]"
        )
    return temp_c


def validate_u_value(u: float, name: str = "U-value") -> float:
    """Ensure *u* is a plausible thermal transmittance (0 < U ≤ 10 W/m²K).

    Raises
    ------
    ValidationError
    """
    if not (0 < u <= 10.0):
        raise ValidationError(
            f"{name} = {u} W/(m²·K) is outside plausible range (0, 10]"
        )
    return u


def validate_area(area_m2: float, name: str = "area") -> float:
    """Ensure *area_m2* is a plausible building area.

    Raises
    ------
    ValidationError
    """
    if not (0 < area_m2 <= 1_000_000):
        raise ValidationError(
            f"{name} = {area_m2} m² is outside plausible range"
        )
    return area_m2
