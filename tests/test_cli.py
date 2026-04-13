"""Tests for the command-line interface."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from ai_hvac.cli import app

runner = CliRunner()


class TestCLI:
    """Smoke tests for the Typer entry point."""

    def test_version_command(self) -> None:
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert result.stdout.strip() == "0.1.0"

    def test_load_calc_command(self) -> None:
        result = runner.invoke(
            app,
            [
                "load-calc",
                "--heated-area-m2",
                "480",
                "--wall-area-m2",
                "320",
                "--roof-area-m2",
                "160",
                "--floor-area-m2",
                "160",
                "--window-area-m2",
                "70",
            ],
        )
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["total_heating_load_kw"] > 0
        assert payload["specific_load_w_per_m2"] > 0
