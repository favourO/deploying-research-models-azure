"""Pure, infrastructure-independent financial analysis."""

from src.analysis.exceptions import (
    AnalysisError,
    InsufficientObservationsError,
    InvalidPriceError,
)
from src.analysis.models import SummaryStatistics
from src.analysis.statistics import (
    calculate_cumulative_return,
    calculate_mean_return,
    calculate_returns,
    calculate_summary_statistics,
    calculate_volatility,
)

__all__ = [
    "AnalysisError",
    "InsufficientObservationsError",
    "InvalidPriceError",
    "SummaryStatistics",
    "calculate_cumulative_return",
    "calculate_mean_return",
    "calculate_returns",
    "calculate_summary_statistics",
    "calculate_volatility",
]
