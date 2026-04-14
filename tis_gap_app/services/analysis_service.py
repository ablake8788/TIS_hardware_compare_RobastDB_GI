"""
Application service implementing the technology gap analysis use case.
Orchestrates: input validation → LLM comparison → rendering → persistence → email.
All external I/O occurs through ports.
"""
import os
import logging
from datetime import datetime

from domain.models import AnalysisInputs, AnalysisResult
from domain.errors import ValidationError
from ports.llm import LLMPort

logger = logging.getLogger(__name__)


class AnalysisService:
    """Primary use case orchestrator."""

    def __init__(self, llm_port: LLMPort, reports_dir: str = "reports",
                 emailer=None, cfg=None):
        self._llm        = llm_port
        self._reports_dir = reports_dir
        self._emailer    = emailer   # optional EmailerPort
        self._cfg        = cfg       # optional AppSettings
        os.makedirs(reports_dir, exist_ok=True)

    def run(self, inputs: AnalysisInputs) -> AnalysisResult:
        # 1. Validate inputs
        self._validate(inputs)

        # 2. Call LLM via port
        rows = self._llm.compare(inputs)

        # 3. Assemble result
        result = AnalysisResult(
            run_id=inputs.run_id,
            competitor=inputs.competitor,
            rows=rows,
            generated_at=datetime.now(),
        )

        # 4. Send email notification if enabled
        if self._emailer and self._cfg and self._cfg.email and self._cfg.email.enabled:
            self._send_notification(result)

        return result

    def _send_notification(self, result: AnalysisResult) -> None:
        """Send email notification with report. Non-fatal if it fails."""
        try:
            from services.email_builder import build_report_email
            message = build_report_email(result, self._cfg)
            success = self._emailer.send(message)
            if success:
                logger.info(f"Email notification sent for run {result.run_id}")
            else:
                logger.warning(f"Email notification failed for run {result.run_id}")
        except Exception as e:
            logger.error(f"Email notification error: {e}")

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
