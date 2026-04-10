"""
Application service implementing the technology gap analysis use case.
Orchestrates: input validation → LLM comparison → rendering → persistence.
All external I/O occurs through ports.
"""
import os
from datetime import datetime

from domain.models import AnalysisInputs, AnalysisResult
from domain.errors import ValidationError
from ports.llm import LLMPort


class AnalysisService:
    """Primary use case orchestrator."""

    def __init__(self, llm_port: LLMPort, reports_dir: str = "reports"):
        self._llm = llm_port
        self._reports_dir = reports_dir
        os.makedirs(reports_dir, exist_ok=True)

    def run(self, inputs: AnalysisInputs) -> AnalysisResult:
        # 1. Validate inputs
        self._validate(inputs)

        # 2. Call LLM via port (ports.llm → adapter)
        rows = self._llm.compare(inputs)

        # 3. Assemble result
        result = AnalysisResult(
            run_id=inputs.run_id,
            competitor=inputs.competitor,
            rows=rows,
            generated_at=datetime.now(),
        )

        return result

    def _validate(self, inputs: AnalysisInputs) -> None:
        if not inputs.hardware_list:
            raise ValidationError("Hardware list is empty.")
        if not inputs.competitor.name:
            raise ValidationError("Competitor name is required.")
        for item in inputs.hardware_list:
            if not item.name.strip():
                raise ValidationError("All hardware rows must have a name.")
            if item.titanium not in ("Yes", "No"):
                raise ValidationError(
                    f"Hardware '{item.name}': Titanium field must be Yes or No."
                )
