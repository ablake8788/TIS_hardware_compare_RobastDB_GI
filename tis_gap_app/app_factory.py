"""
Composition root.
Wires port interfaces to concrete adapters — including emailer.
No business logic here.
"""
import os
from config.ini_config import get_settings
from services.analysis_service import AnalysisService

_ini_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tis_gap_app.ini')
_cfg = get_settings(ini_path=_ini_path)


def create_app_services(provider: str = "openai", api_key_override: str = "") -> AnalysisService:
    """
    Wire concrete adapters to ports and return a ready AnalysisService.
    Config priority: api_key_override → INI file → environment variable.
    """
    reports_dir = _cfg.report_location

    # ── LLM adapter ──────────────────────────────────────────────────────────
    if provider == "anthropic":
        from adapters.llm_anthropic import AnthropicAdapter
        api_key = api_key_override or os.environ.get("ANTHROPIC_API_KEY", "")
        llm_port = AnthropicAdapter(api_key=api_key)
    else:
        from adapters.llm_openai import OpenAIAdapter
        api_key = (
            api_key_override
            or _cfg.openai.api_key
            or os.environ.get("OPENAI_API_KEY", "")
        )
        llm_port = OpenAIAdapter(api_key=api_key, model=_cfg.openai.model)

    # ── Email adapter (optional) ──────────────────────────────────────────────
    emailer = None
    if _cfg.email and _cfg.email.enabled:
        from adapters.email_smtp import SMTPEmailer
        emailer = SMTPEmailer(
            smtp_server  = _cfg.email.smtp_server,
            smtp_port    = _cfg.email.smtp_port,
            smtp_user    = _cfg.email.smtp_user,
            smtp_password= _cfg.email.smtp_password,
        )

    return AnalysisService(
        llm_port    = llm_port,
        reports_dir = reports_dir,
        emailer     = emailer,
        cfg         = _cfg,
    )
