"""Tests for the rule-based system recommender."""

from __future__ import annotations

from ai_hvac.hvac.load_calc import ClimateZone, LoadResult
from ai_hvac.hvac.system_design import SystemDesigner


class TestSystemDesigner:
    """Behavioural tests for ranking heuristics."""

    def test_large_load_can_surface_district_heating(self) -> None:
        load = LoadResult(total_heating_load_w=250_000, specific_load_w_per_m2=90.0)
        recommendations = SystemDesigner(
            climate_zone=ClimateZone.MODERATE_COLD,
            building_type="office",
            load_result=load,
        ).recommend(top_n=5)
        system_keys = [recommendation.system_key for recommendation in recommendations]
        assert "district_heating" in system_keys

    def test_building_type_changes_top_rank(self) -> None:
        load = LoadResult(total_heating_load_w=50_000, specific_load_w_per_m2=50.0)
        residential_top = SystemDesigner(
            climate_zone=ClimateZone.MODERATE_COLD,
            building_type="residential",
            load_result=load,
        ).recommend(top_n=1)[0]
        hospital_top = SystemDesigner(
            climate_zone=ClimateZone.MODERATE_COLD,
            building_type="hospital",
            load_result=load,
        ).recommend(top_n=1)[0]
        assert residential_top.system_key != hospital_top.system_key
