"""
Composition root.
This module wires port interfaces to concrete adapters.
No business logic should appear here.
"""
import os

from services.analysis_service import AnalysisService


def create_app_services(provider: str = "openai") -> AnalysisService:
    """
    Wire concrete adapters to ports and return a ready AnalysisService.

    provider: "openai" | "anthropic"
    """
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")

    if provider == "anthropic":
        from adapters.llm_anthropic import AnthropicAdapter
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        llm_port = AnthropicAdapter(api_key=api_key)
    else:
        from adapters.llm_openai import OpenAIAdapter
        api_key = os.environ.get("OPENAI_API_KEY", "")
        llm_port = OpenAIAdapter(api_key=api_key)

    return AnalysisService(llm_port=llm_port, reports_dir=reports_dir)
