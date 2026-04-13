"""Tests for the heating-load calculator."""

from __future__ import annotations

import pytest

from ai_hvac.core.exceptions import ValidationError
from ai_hvac.hvac.load_calc import ClimateZone, EnvelopeSpec, HeatingLoadCalculator, LoadResult


@pytest.fixture()
def residential_envelope() -> EnvelopeSpec:
    """Typical post-2000 residential envelope."""
    return EnvelopeSpec(
        wall_area_m2=300,
        roof_area_m2=150,
        floor_area_m2=150,
        window_area_m2=60,
        u_wall=0.28,
        u_roof=0.20,
        u_floor=0.35,
        u_window=1.30,
    )


@pytest.fixture()
def calculator() -> HeatingLoadCalculator:
    return HeatingLoadCalculator(
        climate_zone=ClimateZone.MODERATE_COLD,
        building_type="residential",
        heated_area_m2=450,
    )


class TestHeatingLoadCalculator:
    """Unit tests for HeatingLoadCalculator."""

    def test_basic_calculation_returns_load_result(
        self, calculator: HeatingLoadCalculator, residential_envelope: EnvelopeSpec
    ) -> None:
        result = calculator.calculate(residential_envelope)
        assert isinstance(result, LoadResult)

    def test_total_load_is_positive(
        self, calculator: HeatingLoadCalculator, residential_envelope: EnvelopeSpec
    ) -> None:
        result = calculator.calculate(residential_envelope)
        assert result.total_heating_load_w > 0
        assert result.total_heating_load_kw > 0

    def test_transmission_exceeds_ventilation(
        self, calculator: HeatingLoadCalculator, residential_envelope: EnvelopeSpec
    ) -> None:
        result = calculator.calculate(residential_envelope)
        assert result.transmission_loss_w > result.ventilation_loss_w

    def test_specific_load_in_plausible_range(
        self, calculator: HeatingLoadCalculator, residential_envelope: EnvelopeSpec
    ) -> None:
        result = calculator.calculate(residential_envelope)
        assert 10 < result.specific_load_w_per_m2 < 150

    def test_safety_factor_increases_load(
        self, calculator: HeatingLoadCalculator, residential_envelope: EnvelopeSpec
    ) -> None:
        result_no_safety = calculator.calculate(residential_envelope, safety_factor=1.0)
        result_with_safety = calculator.calculate(residential_envelope, safety_factor=1.15)
        assert result_with_safety.total_heating_load_w > result_no_safety.total_heating_load_w

    def test_cold_climate_higher_load(self, residential_envelope: EnvelopeSpec) -> None:
        calc_cold = HeatingLoadCalculator(
            climate_zone=ClimateZone.COLD,
            heated_area_m2=450,
        )
        calc_mild = HeatingLoadCalculator(
            climate_zone=ClimateZone.MILD,
            heated_area_m2=450,
        )
        result_cold = calc_cold.calculate(residential_envelope)
        result_mild = calc_mild.calculate(residential_envelope)
        assert result_cold.total_heating_load_w > result_mild.total_heating_load_w

    def test_assumptions_are_populated(
        self, calculator: HeatingLoadCalculator, residential_envelope: EnvelopeSpec
    ) -> None:
        result = calculator.calculate(residential_envelope)
        assert len(result.assumptions) > 0
        assert any("Indoor" in assumption for assumption in result.assumptions)

    def test_zero_heated_area_is_rejected(self, residential_envelope: EnvelopeSpec) -> None:
        with pytest.raises(ValidationError):
            HeatingLoadCalculator(
                climate_zone=ClimateZone.MODERATE_COLD,
                heated_area_m2=0,
            )

    def test_negative_ventilation_rate_is_rejected(
        self, calculator: HeatingLoadCalculator, residential_envelope: EnvelopeSpec
    ) -> None:
        with pytest.raises(ValidationError):
            calculator.calculate(residential_envelope, ventilation_rate_ach=-0.1)

    def test_invalid_envelope_area_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            EnvelopeSpec(
                wall_area_m2=0,
                roof_area_m2=150,
                floor_area_m2=150,
                window_area_m2=60,
            )


class TestClimateZone:
    """Tests for climate zone enum."""

    def test_design_temperatures_are_ordered(self) -> None:
        assert ClimateZone.COLD.design_outdoor_temp < ClimateZone.MILD.design_outdoor_temp

    @pytest.mark.parametrize("zone", list(ClimateZone))
    def test_all_zones_have_design_temp(self, zone: ClimateZone) -> None:
        assert isinstance(zone.design_outdoor_temp, float)
