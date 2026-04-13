"""LLM module — OpenAI client, prompt templates, and output parsers."""

from ai_hvac.llm.client import HVACAssistant
from ai_hvac.llm.prompts import PromptLibrary

__all__ = ["HVACAssistant", "PromptLibrary"]
