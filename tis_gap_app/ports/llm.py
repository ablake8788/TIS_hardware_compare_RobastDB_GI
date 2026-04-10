from abc import ABC, abstractmethod
from typing import List
from domain.models import ComparisonRow, AnalysisInputs


class LLMPort(ABC):
    """Abstract interface for LLM-based comparison."""

    @abstractmethod
    def compare(self, inputs: AnalysisInputs) -> List[ComparisonRow]:
        """Run comparison and return list of ComparisonRow."""
        ...
