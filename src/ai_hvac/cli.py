"""Command-line interface for AI HVAC Design Assistant."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ai_hvac import __version__
from ai_hvac.hvac.load_calc import ClimateZone, EnvelopeSpec, HeatingLoadCalculator
from ai_hvac.llm.client import HVACAssistant
from ai_hvac.simulation.polysun import PolysunTemplateGenerator

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="AI HVAC Design Assistant command-line tools.",
)


def _echo_json(payload: dict[str, object]) -> None:
    """Print JSON in a console-safe format."""
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))


@app.command()
def version() -> None:
    """Print the installed package version."""
    typer.echo(__version__)


@app.command("load-calc")
def load_calc(
    heated_area_m2: Annotated[float, typer.Option(help="Gross heated floor area in m2.")],
    wall_area_m2: Annotated[float, typer.Option(help="External wall area in m2.")],
    roof_area_m2: Annotated[float, typer.Option(help="Roof area in m2.")],
    floor_area_m2: Annotated[float, typer.Option(help="Ground-contact floor area in m2.")],
    window_area_m2: Annotated[float, typer.Option(help="Window area in m2.")],
    climate_zone: Annotated[
        ClimateZone,
        typer.Option(case_sensitive=False, help="Simplified climate zone."),
    ] = ClimateZone.MODERATE_COLD,
    building_type: Annotated[str, typer.Option(help="Building usage type.")] = "residential",
    ventilation_rate_ach: Annotated[float, typer.Option(help="Air changes per hour.")] = 0.5,
    room_height_m: Annotated[float, typer.Option(help="Average room height in metres.")] = 2.7,
    safety_factor: Annotated[float, typer.Option(help="Multiplicative safety factor.")] = 1.15,
    u_wall: Annotated[float, typer.Option(help="Wall U-value in W/(m2K).")] = 0.28,
    u_roof: Annotated[float, typer.Option(help="Roof U-value in W/(m2K).")] = 0.20,
    u_floor: Annotated[float, typer.Option(help="Floor U-value in W/(m2K).")] = 0.35,
    u_window: Annotated[float, typer.Option(help="Window U-value in W/(m2K).")] = 1.30,
) -> None:
    """Run a deterministic heating-load calculation."""
    calculator = HeatingLoadCalculator(
        climate_zone=climate_zone,
        building_type=building_type,
        heated_area_m2=heated_area_m2,
    )
    envelope = EnvelopeSpec(
        wall_area_m2=wall_area_m2,
        roof_area_m2=roof_area_m2,
        floor_area_m2=floor_area_m2,
        window_area_m2=window_area_m2,
        u_wall=u_wall,
        u_roof=u_roof,
        u_floor=u_floor,
        u_window=u_window,
    )
    result = calculator.calculate(
        envelope,
        ventilation_rate_ach=ventilation_rate_ach,
        room_height_m=room_height_m,
        safety_factor=safety_factor,
    )
    _echo_json(
        {
            "transmission_loss_w": result.transmission_loss_w,
            "ventilation_loss_w": result.ventilation_loss_w,
            "total_heating_load_w": result.total_heating_load_w,
            "total_heating_load_kw": result.total_heating_load_kw,
            "specific_load_w_per_m2": result.specific_load_w_per_m2,
            "assumptions": result.assumptions,
        }
    )


@app.command("polysun-template")
def polysun_template(
    heating_load_kw: Annotated[float, typer.Option(help="Peak design heating load in kW.")],
    building_type: Annotated[str, typer.Option(help="Building usage type.")] = "residential",
    dhw_demand_litres_day: Annotated[
        float, typer.Option(help="Daily DHW demand in litres.")
    ] = 200.0,
    hp_type: Annotated[str, typer.Option(help="air_source or ground_source.")] = "air_source",
    with_solar: Annotated[
        bool, typer.Option(help="Include solar or PVT collector loop.")
    ] = False,
) -> None:
    """Generate a Polysun-oriented template as JSON."""
    generator = PolysunTemplateGenerator(
        heating_load_kw=heating_load_kw,
        building_type=building_type,
        dhw_demand_litres_day=dhw_demand_litres_day,
    )
    template = generator.heat_pump_template(hp_type=hp_type, with_solar=with_solar)
    _echo_json(template.to_dict())


@app.command("recommend-system")
def recommend_system(
    building_type: Annotated[str, typer.Option(help="Building usage type.")],
    location: Annotated[str, typer.Option(help="Project location.")],
    heated_area_m2: Annotated[float, typer.Option(help="Gross heated floor area in m2.")],
    cooling_required: Annotated[
        bool, typer.Option(help="Whether active cooling is required.")
    ] = False,
    dhw_required: Annotated[
        bool, typer.Option(help="Whether DHW production is required.")
    ] = True,
    additional_context: Annotated[str, typer.Option(help="Free-form project notes.")] = "",
) -> None:
    """Request an AI-generated system recommendation."""
    result = HVACAssistant().recommend_system(
        building_type=building_type,
        location=location,
        heated_area_m2=heated_area_m2,
        cooling_required=cooling_required,
        dhw_required=dhw_required,
        additional_context=additional_context,
    )
    _echo_json(
        {
            "system_type": result.system_type,
            "components": result.components,
            "estimated_cop": result.estimated_cop,
            "rationale": result.rationale,
            "warnings": result.warnings,
        }
    )


if __name__ == "__main__":
    app()
