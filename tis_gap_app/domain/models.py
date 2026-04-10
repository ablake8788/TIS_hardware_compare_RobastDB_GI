from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class HardwareItem:
    name: str
    description: str
    titanium: str  # "Yes" or "No"


@dataclass
class CompetitorConfig:
    name: str
    url: str
    slug: str


@dataclass
class ComparisonRow:
    hardware: str
    description: str
    companies_using: str
    titanium: str        # Yes / No
    competitor: str      # Yes / Partial / No
    competitor_notes: str


@dataclass
class AnalysisInputs:
    competitor: CompetitorConfig
    hardware_list: List[HardwareItem]
    companies_in_scope: List[str]
    run_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))


@dataclass
class AnalysisResult:
    run_id: str
    competitor: CompetitorConfig
    rows: List[ComparisonRow]
    generated_at: datetime = field(default_factory=datetime.now)
    docx_path: Optional[str] = None

    @property
    def yes_count(self):
        return sum(1 for r in self.rows if r.competitor == "Yes")

    @property
    def partial_count(self):
        return sum(1 for r in self.rows if r.competitor == "Partial")

    @property
    def no_count(self):
        return sum(1 for r in self.rows if r.competitor == "No")

    @property
    def total(self):
        return len(self.rows)
