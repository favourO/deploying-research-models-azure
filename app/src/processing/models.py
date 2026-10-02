"""Data models at the processing boundary."""

from dataclasses import dataclass
from datetime import date

from src.analysis.models import SummaryStatistics


@dataclass(frozen=True, slots=True)
class PriceObservation:
    ticker: str
    date: date
    price: float
    volume: int


@dataclass(frozen=True, slots=True)
class SecurityAnalysisResult:
    ticker: str
    summary: SummaryStatistics
