"""
Adapter: implements ports.llm.LLMPort using the Anthropic API.
Drop-in alternative to OpenAIAdapter — swap in app_factory.py.
"""
import json
import re
from typing import List

import anthropic

from domain.models import AnalysisInputs, ComparisonRow
from domain.errors import LLMError
from ports.llm import LLMPort
from services.prompt_builder import build_prompt


class AnthropicAdapter(LLMPort):
    def __init__(self, api_key: str, model: str = "claude-opus-4-6"):
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def compare(self, inputs: AnalysisInputs) -> List[ComparisonRow]:
        prompt = build_prompt(inputs)
        try:
            message = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as e:
            raise LLMError(f"Anthropic call failed: {e}") from e

        raw = message.content[0].text if message.content else ""
        return self._parse(raw)

    def _parse(self, raw: str) -> List[ComparisonRow]:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            data = json.loads(clean)
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse LLM JSON: {e}\nRaw:\n{raw}") from e

        rows = []
        for item in data:
            rows.append(ComparisonRow(
                hardware=str(item.get("hardware", "")),
                description=str(item.get("description", "")),
                companies_using=str(item.get("companies_using", "None")),
                titanium=str(item.get("titanium", "No")),
                competitor=str(item.get("competitor", "No")),
                competitor_notes=str(item.get("competitor_notes", "")),
            ))
        return rows
