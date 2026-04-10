# TIS Hardware Gap Analysis — Python Flask Application

Competitive hardware comparison tool for Titanium.
Architecture: Clean Architecture / Ports & Adapters (Hexagonal).

---

## Quick Start

### 1. Install dependencies

```bash
cd tis_gap_app
pip install -r requirements.txt
```

### 2. Set your API key (choose one)

**Option A — environment variable (recommended):**
```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# OR Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-...
```

**Option B — paste it in the UI** at Step 01 › Configure.

### 3. Run the app

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## How to use

| Step | Action |
|------|--------|
| 01 Configure | Pick a competitor from the dropdown (PointCentral, EnTouch, SmartRent, 75F, Pelican, Kairos) or add a custom one. Choose OpenAI or Anthropic. |
| 02 Hardware List | Review or edit Titanium's hardware list. Mark each row Yes/No for whether Titanium uses it. |
| 03 Run Analysis | Click "Start analysis". The AI compares the competitor against Titanium's list. |
| 04 Results | View the comparison table in-browser. Filter by Yes / Partial / No. Download the Word report. |

---

## Project structure

```
tis_gap_app/
│
├── app.py                      # Flask app — delivery layer (controller + routes)
├── app_factory.py              # Composition root — wires ports to adapters
├── requirements.txt
│
├── config/
│   └── presets.py              # Preset competitors + default hardware list
│
├── domain/
│   ├── models.py               # Pure dataclasses: HardwareItem, AnalysisInputs, AnalysisResult, etc.
│   └── errors.py               # ValidationError, FatalError, LLMError
│
├── ports/
│   └── llm.py                  # Abstract LLMPort interface
│
├── adapters/
│   ├── llm_openai.py           # OpenAI adapter (implements LLMPort)
│   └── llm_anthropic.py        # Anthropic adapter (implements LLMPort)
│
├── services/
│   ├── analysis_service.py     # Use case orchestrator
│   └── prompt_builder.py       # Pure prompt construction — no I/O
│
├── renderers/
│   └── docx_renderer.py        # Renders AnalysisResult → .docx Word report
│
├── templates/
│   └── index.html              # Jinja2 HTML — 4-step wizard UI
│
├── static/
│   ├── css/style.css           # All styling
│   └── js/app.js               # Frontend logic
│
└── reports/                    # Generated .docx files (auto-created)
```

---

## Swapping LLM providers

The app uses Ports & Adapters. To switch LLM:

- In the UI: change the **LLM provider** dropdown on Step 01.
- In code: edit `app_factory.py` — change `provider` default or add a new adapter in `adapters/`.

---

## Adding competitors

Edit `config/presets.py`:

```python
CompetitorConfig(name="NewCo", url="https://newco.com", slug="newco"),
```

Restart the app — the new competitor appears in the dropdown automatically.

---

## Adding hardware rows

Either edit `DEFAULT_HARDWARE` in `config/presets.py`, or add rows directly in the UI at Step 02.

---

## Report output

Generated `.docx` files are saved in the `reports/` folder with naming:
```
gap_analysis_{competitor}_{YYYYMMDD_HHMMSS}.docx
```

The Word report includes:
- Title block with competitor and date
- Executive summary cards (totals, Yes / Partial / No counts)
- Color-coded hardware comparison table (green / yellow / red)
- Disclaimer footer
