"""
Pure prompt composition.
No network, filesystem, or external dependencies.
Changes here alter only the LLM request payload.
"""
from domain.models import AnalysisInputs


def build_prompt(inputs: AnalysisInputs) -> str:
    comp = inputs.competitor
    companies_str = ", ".join(inputs.companies_in_scope)

    hw_rows = "\n".join(
        f"| {item.name} | {item.description} | {item.titanium} |"
        for item in inputs.hardware_list
    )

    return f"""You are a hardware analyst for smart building / proptech technology.

Titanium hardware list:
| Hardware | Description | Titanium uses? |
|---|---|---|
{hw_rows}

Competitor: {comp.name}
Competitor website: {comp.url}
Companies in scope: {companies_str}

TASK:
For each hardware row, produce a JSON array. Each element must be:
{{
  "hardware": "<exact hardware name from list>",
  "description": "<concise business-friendly description, max 15 words>",
  "companies_using": "<comma-separated subset of [{companies_str}] known to use this hardware, or None>",
  "titanium": "<Yes or No, copied exactly from input>",
  "competitor": "<Yes, Partial, or No — for {comp.name}>",
  "competitor_notes": "<1 sentence reason for Partial or No; empty string for Yes>"
}}

COMPARISON RULES:
1. Titanium: copy exactly from input (Yes or No). Never change this.
2. {comp.name} column:
   - Yes = competitor clearly offers this as a standalone hardware device.
   - Partial = competitor has limited, integrated, bundled, or indirect support.
   - No = competitor does not offer this hardware.
3. companies_using: list only companies from [{companies_str}] with reasonable known usage. Be conservative.
4. Separate hardware devices differ from bundled/integrated capability.
   Example: if Titanium has separate CO2, VOC, temp sensors, that does NOT make Titanium an "IAQ Multi-Sensor".
   Example: if {comp.name} integrates IAQ into a thermostat, that is Partial unless sold standalone.
5. Water Valve, Leak Detection, Energy Metering — treat these as distinct hardware categories.
6. Be conservative. When in doubt, prefer Partial over Yes.

Return ONLY the JSON array. No markdown fences. No preamble. No trailing text.
"""
