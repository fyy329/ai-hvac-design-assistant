"""Tests for unit converters."""

import pytest

from ai_hvac.utils.converters import UnitConverter


class TestTemperature:
    def test_celsius_to_kelvin(self) -> None:
        assert UnitConverter.celsius_to_kelvin(0) == pytest.approx(273.15)
        assert UnitConverter.celsius_to_kelvin(100) == pytest.approx(373.15)

    def test_kelvin_to_celsius(self) -> None:
        assert UnitConverter.kelvin_to_celsius(273.15) == pytest.approx(0)

    def test_fahrenheit_to_celsius(self) -> None:
        assert UnitConverter.fahrenheit_to_celsius(32) == pytest.approx(0)
        assert UnitConverter.fahrenheit_to_celsius(212) == pytest.approx(100)

    def test_celsius_to_fahrenheit(self) -> None:
        assert UnitConverter.celsius_to_fahrenheit(0) == pytest.approx(32)
        assert UnitConverter.celsius_to_fahrenheit(100) == pytest.approx(212)

    def test_roundtrip(self) -> None:
        original = 20.0
        assert UnitConverter.kelvin_to_celsius(
            UnitConverter.celsius_to_kelvin(original)
        ) == pytest.approx(original)


class TestEnergy:
    def test_kw_to_btu_h(self) -> None:
        assert UnitConverter.kw_to_btu_h(1) == pytest.approx(3412.14, rel=1e-3)

    def test_btu_h_to_kw(self) -> None:
        assert UnitConverter.btu_h_to_kw(3412.14) == pytest.approx(1.0, rel=1e-3)

    def test_kwh_mj_roundtrip(self) -> None:
        original = 100.0
        assert UnitConverter.mj_to_kwh(UnitConverter.kwh_to_mj(original)) == pytest.approx(original)


class TestPressure:
    def test_bar_to_pa(self) -> None:
        assert UnitConverter.bar_to_pa(1) == pytest.approx(100_000)

    def test_pa_to_bar(self) -> None:
        assert UnitConverter.pa_to_bar(100_000) == pytest.approx(1)


class TestUValue:
    def test_r_to_u_round_trip(self) -> None:
        u_original = 0.28
        r = UnitConverter.u_value_to_r_value(u_original)
        u_back = UnitConverter.r_value_to_u_value(r)
        assert u_back == pytest.approx(u_original, rel=1e-3)

    def test_zero_protection(self) -> None:
        assert UnitConverter.r_value_to_u_value(0) == 0.0
        assert UnitConverter.u_value_to_r_value(0) == 0.0


class TestFlow:
    def test_m3h_to_ls(self) -> None:
        assert UnitConverter.m3h_to_ls(3.6) == pytest.approx(1.0)

    def test_ls_to_m3h(self) -> None:
        assert UnitConverter.ls_to_m3h(1.0) == pytest.approx(3.6)
