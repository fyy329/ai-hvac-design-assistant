"""
AI HVAC Design Assistant
========================

An AI-powered toolkit for HVAC system design, load calculation,
and building energy simulation automation.

Modules
-------
core : Configuration management and shared exceptions.
llm  : OpenAI API client, HVAC-domain prompt templates, and output parsers.
hvac : Heating/cooling load calculators and system design recommenders.
simulation : Template generators for Polysun and Modelica workflows.
utils : Unit converters, input validators, and helper functions.
"""

__version__ = "0.1.0"
__author__ = "fyy329"

from ai_hvac.core.config import Settings
from ai_hvac.hvac.load_calc import HeatingLoadCalculator
from ai_hvac.llm.client import HVACAssistant

__all__ = [
    "Settings",
    "HeatingLoadCalculator",
    "HVACAssistant",
]
