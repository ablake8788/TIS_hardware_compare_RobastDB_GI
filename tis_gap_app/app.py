# Every folder that contains Python files you import from needs one:
# tis_gap_app\
#   config\
#     __init__.py       ← needed so you can do: from config.ini_config import ...
#     ini_config.py
#     presets.py
#   domain\
#     __init__.py       ← needed so you can do: from domain.models import ...
#     models.py
#   services\
#     __init__.py       ← needed
#     analysis_service.py
#   adapters\
#     __init__.py       ← needed
#     llm_openai.py
#   renderers\
#     __init__.py       ← needed
#     docx_renderer.py
#   ports\
#     __init__.py       ← needed
#     llm.py
# They can be completely empty files — just their presence is enough. Think of them as a flag that says "this folder is a Python package, imports are allowed."



"""
Flask web application - delivery layer.
Controller translates HTTP requests into domain Inputs, calls the use case,
handles errors, and returns responses.
"""
import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.ini_config import get_settings
##from tis_gap_app.app_factory import create_app_services
from app_factory import create_app_services
from config.presets import COMPETITORS, COMPANIES_IN_SCOPE, DEFAULT_HARDWARE
from domain.models import AnalysisInputs, HardwareItem, CompetitorConfig
from domain.errors import ValidationError, LLMError
from renderers.docx_renderer import render_docx

# ── Load INI config ───────────────────────────────────────────────────────────
_ini_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tis_gap_app.ini')
_cfg = get_settings(ini_path=_ini_path)

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "tis-gap-dev-secret-2024")

REPORTS_DIR = _cfg.report_location
os.makedirs(REPORTS_DIR, exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_service(provider: str, api_key_override: str = ""):
    return create_app_services(provider=provider, api_key_override=api_key_override)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template(
        "index.html",
        competitors=COMPETITORS,
        default_hardware=DEFAULT_HARDWARE,
        companies=COMPANIES_IN_SCOPE,
    )


@app.route("/api/config")
def get_config():
    cfg = get_settings(ini_path=_ini_path)
    return jsonify({
        "ini_loaded": True,
        "model": cfg.openai.model,
        "api_key_set": bool(cfg.openai.api_key),
        "report_location": cfg.report_location,
        "baseline_url": cfg.baseline_url,
        "email_enabled": cfg.email.enabled if cfg.email else False,
        "email_to": cfg.email.to_email if cfg.email else [],
        "outputs": {
            "docx": cfg.outputs.docx_enabled,
            "pptx": cfg.outputs.pptx_enabled,
            "html": cfg.outputs.html_enabled,
            "md":   cfg.outputs.md_enabled,
        },
        "sqlserver_configured": cfg.sqlserver is not None,
    })


@app.route("/api/hardware/defaults", methods=["GET"])
def get_default_hardware():
    return jsonify([
        {"name": h.name, "description": h.description, "titanium": h.titanium}
        for h in DEFAULT_HARDWARE
    ])


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)

    # ── Competitor ────────────────────────────────────────────────────────────
    comp_slug   = data.get("competitor_slug", "")
    custom_name = data.get("custom_competitor_name", "").strip()
    custom_url  = data.get("custom_competitor_url", "").strip()

    comp_map = {c.slug: c for c in COMPETITORS}
    if comp_slug and comp_slug in comp_map:
        competitor = comp_map[comp_slug]
    elif custom_name:
        competitor = CompetitorConfig(
            name=custom_name,
            url=custom_url or f"https://{custom_name.lower().replace(' ', '')}.com",
            slug=custom_name.lower().replace(" ", "_"),
        )
    else:
        return jsonify({"error": "No competitor selected."}), 400

    # ── Hardware list ─────────────────────────────────────────────────────────
    hw_raw = data.get("hardware", [])
    try:
        hardware_list = [
            HardwareItem(
                name=item["name"].strip(),
                description=item["description"].strip(),
                titanium=item["titanium"].strip(),
            )
            for item in hw_raw
            if item.get("name", "").strip()
        ]
    except (KeyError, TypeError) as e:
        return jsonify({"error": f"Malformed hardware data: {e}"}), 400

    # ── Provider + API key ────────────────────────────────────────────────────
    provider         = data.get("provider", "openai")
    api_key_override = data.get("api_key", "").strip()

    # ── Build inputs & run ────────────────────────────────────────────────────
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    inputs = AnalysisInputs(
        competitor=competitor,
        hardware_list=hardware_list,
        companies_in_scope=COMPANIES_IN_SCOPE,
        run_id=run_id,
    )

    try:
        service = _get_service(provider, api_key_override)
        result  = service.run(inputs)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 422
    except LLMError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500

    # ── Render DOCX ───────────────────────────────────────────────────────────
    filename  = f"gap_analysis_{competitor.slug}_{run_id}.docx"
    docx_path = os.path.join(REPORTS_DIR, filename)
    render_docx(result, docx_path)
    result.docx_path = filename

    return jsonify({
        "run_id":       result.run_id,
        "competitor":   result.competitor.name,
        "generated_at": result.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total":   result.total,
            "yes":     result.yes_count,
            "partial": result.partial_count,
            "no":      result.no_count,
        },
        "rows": [
            {
                "hardware":         r.hardware,
                "description":      r.description,
                "companies_using":  r.companies_using,
                "titanium":         r.titanium,
                "competitor":       r.competitor,
                "competitor_notes": r.competitor_notes,
            }
            for r in result.rows
        ],
        "docx_filename": filename,
    })


@app.route("/download/<filename>")
def download(filename):
    safe = os.path.basename(filename)
    path = os.path.join(REPORTS_DIR, safe)
    if not os.path.exists(path):
        return "File not found.", 404
    return send_file(path, as_attachment=True, download_name=safe)


if __name__ == "__main__":
    print("=" * 45)
    print("  TIS Hardware Gap Analysis")
    print(f"  Model      : {_cfg.openai.model}")
    print(f"  API key    : {'SET' if _cfg.openai.api_key else 'NOT SET - enter in UI'}")
    print(f"  Reports    : {REPORTS_DIR}")
    print(f"  Email      : {'ON' if _cfg.email and _cfg.email.enabled else 'OFF'}")
    print("  URL        : http://localhost:5000")
    print("=" * 45)
    app.run(debug=False, port=5000, host="0.0.0.0")

##################################################################################

# """
# Flask web application — delivery layer.
# Controller translates HTTP requests into domain Inputs, calls the use case,
# handles errors, and returns responses.
# """
#
# """
# Flask web application - delivery layer.
# """
#
# import os
# import sys
# from datetime import datetime
# from flask import Flask, render_template, request, jsonify, send_file
#
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
#
# from config.ini_config import get_settings
# from app_factory import create_app_services
# from config.presets import COMPETITORS, COMPANIES_IN_SCOPE, DEFAULT_HARDWARE
# from domain.models import AnalysisInputs, HardwareItem, CompetitorConfig
# from domain.errors import ValidationError, LLMError
# from renderers.docx_renderer import render_docx
#
# _ini_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tis_gap_app.ini')
# _cfg = get_settings(ini_path=_ini_path)
#
# app = Flask(__name__)
# app.secret_key = os.environ.get("FLASK_SECRET", "tis-gap-dev-secret-2024")
#
# REPORTS_DIR = _cfg.report_location
# os.makedirs(REPORTS_DIR, exist_ok=True)
#
#
#
#
#
# app = Flask(__name__)
# app.secret_key = os.environ.get("FLASK_SECRET", "tis-gap-dev-secret-2024")
#
# REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
# os.makedirs(REPORTS_DIR, exist_ok=True)
#
# #####################
# # ; python -c "
# # ;>> import os, sys
# # ;>> sys.path.insert(0, '.')
# # ;>> from config.ini_config import reload_settings
# # ;>> cfg = reload_settings(os.path.join(os.getcwd(), 'tis_gap_app.ini'))
# # ;>> print('Key:', cfg.openai.api_key[:10] if cfg.openai.api_key else 'NOT FOUND')
# # ;>> print('Model:', cfg.openai.model)
# #####################
#
#
# # ── Helpers ──────────────────────────────────────────────────────────────────
#
# def _get_service(provider: str):
#     return create_app_services(provider=provider)
#
#
# # ── Routes ───────────────────────────────────────────────────────────────────
#
#
# @app.route("/api/config")
# def get_config():
#     cfg = get_settings()
#     return jsonify({
#         "ini_loaded": True,
#         "model": cfg.openai.model,
#         "api_key_set": bool(cfg.openai.api_key),
#         "report_location": cfg.report_location,
#         "baseline_url": cfg.baseline_url,
#         "email_enabled": cfg.email.enabled if cfg.email else False,
#         "email_to": cfg.email.to_email if cfg.email else [],
#         "outputs": {
#             "docx": cfg.outputs.docx_enabled,
#             "pptx": cfg.outputs.pptx_enabled,
#             "html": cfg.outputs.html_enabled,
#             "md":   cfg.outputs.md_enabled,
#         },
#         "sqlserver_configured": cfg.sqlserver is not None,
#     })
# @app.route("/")
# def index():
#     return render_template(
#         "index.html",
#         competitors=COMPETITORS,
#         default_hardware=DEFAULT_HARDWARE,
#         companies=COMPANIES_IN_SCOPE,
#     )
#
#
# @app.route("/api/hardware/defaults", methods=["GET"])
# def get_default_hardware():
#     return jsonify([
#         {"name": h.name, "description": h.description, "titanium": h.titanium}
#         for h in DEFAULT_HARDWARE
#     ])
#
#
# @app.route("/api/analyze", methods=["POST"])
# def analyze():
#     data = request.get_json(force=True)
#
#     # ── Parse competitor ──────────────────────────────────────────────────────
#     comp_slug = data.get("competitor_slug", "")
#     custom_name = data.get("custom_competitor_name", "").strip()
#     custom_url  = data.get("custom_competitor_url", "").strip()
#
#     comp_map = {c.slug: c for c in COMPETITORS}
#     if comp_slug and comp_slug in comp_map:
#         competitor = comp_map[comp_slug]
#     elif custom_name:
#         from domain.models import CompetitorConfig
#         competitor = CompetitorConfig(
#             name=custom_name,
#             url=custom_url or f"https://{custom_name.lower().replace(' ', '')}.com",
#             slug=custom_name.lower().replace(" ", "_"),
#         )
#     else:
#         return jsonify({"error": "No competitor selected."}), 400
#
#     # ── Parse hardware list ───────────────────────────────────────────────────
#     hw_raw = data.get("hardware", [])
#     try:
#         hardware_list = [
#             HardwareItem(
#                 name=item["name"].strip(),
#                 description=item["description"].strip(),
#                 titanium=item["titanium"].strip(),
#             )
#             for item in hw_raw
#             if item.get("name", "").strip()
#         ]
#     except (KeyError, TypeError) as e:
#         return jsonify({"error": f"Malformed hardware data: {e}"}), 400
#
#     # ── Parse provider ────────────────────────────────────────────────────────
#     provider = data.get("provider", "openai")
#     api_key  = data.get("api_key", "").strip()
#     if api_key:
#         env_key = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
#         os.environ[env_key] = api_key
#
#     # ── Build inputs & run ────────────────────────────────────────────────────
#     run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
#     inputs = AnalysisInputs(
#         competitor=competitor,
#         hardware_list=hardware_list,
#         companies_in_scope=COMPANIES_IN_SCOPE,
#         run_id=run_id,
#     )
#
#     try:
#         service = _get_service(provider)
#         result  = service.run(inputs)
#     except ValidationError as e:
#         return jsonify({"error": str(e)}), 422
#     except LLMError as e:
#         return jsonify({"error": str(e)}), 502
#     except Exception as e:
#         return jsonify({"error": f"Unexpected error: {e}"}), 500
#
#     # ── Render DOCX ───────────────────────────────────────────────────────────
#     filename = f"gap_analysis_{competitor.slug}_{run_id}.docx"
#     docx_path = os.path.join(REPORTS_DIR, filename)
#     render_docx(result, docx_path)
#     result.docx_path = filename
#
#     # ── Return JSON summary + filename ───────────────────────────────────────
#     return jsonify({
#         "run_id": result.run_id,
#         "competitor": result.competitor.name,
#         "generated_at": result.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
#         "summary": {
#             "total": result.total,
#             "yes": result.yes_count,
#             "partial": result.partial_count,
#             "no": result.no_count,
#         },
#         "rows": [
#             {
#                 "hardware": r.hardware,
#                 "description": r.description,
#                 "companies_using": r.companies_using,
#                 "titanium": r.titanium,
#                 "competitor": r.competitor,
#                 "competitor_notes": r.competitor_notes,
#             }
#             for r in result.rows
#         ],
#         "docx_filename": filename,
#     })
#
#
# @app.route("/download/<filename>")
# def download(filename):
#     # Sanitize filename to prevent directory traversal
#     safe = os.path.basename(filename)
#     path = os.path.join(REPORTS_DIR, safe)
#     if not os.path.exists(path):
#         return "File not found.", 404
#     return send_file(path, as_attachment=True, download_name=safe)
#
#
# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
