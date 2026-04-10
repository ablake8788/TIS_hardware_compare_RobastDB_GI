"""
Adapter: implements ports.llm.LLMPort using the OpenAI API.
Anti-corruption layer — translates internal contracts to/from OpenAI shapes.
"""
import json
import re
from typing import List

from openai import OpenAI

from domain.models import AnalysisInputs, ComparisonRow
from domain.errors import LLMError
from ports.llm import LLMPort
from services.prompt_builder import build_prompt


class OpenAIAdapter(LLMPort):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def compare(self, inputs: AnalysisInputs) -> List[ComparisonRow]:
        prompt = build_prompt(inputs)
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4096,
            )
        except Exception as e:
            raise LLMError(f"OpenAI call failed: {e}") from e

        raw = response.choices[0].message.content or ""
        return self._parse(raw)

    def _parse(self, raw: str) -> List[ComparisonRow]:
        # Strip accidental markdown fences
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
