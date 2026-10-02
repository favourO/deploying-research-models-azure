"""Explicit results returned by the analysis layer."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SummaryStatistics:
    """Summary of simple returns for one ordered price series."""

    observations: int
    returns: tuple[float, ...]
    mean_return: float
    volatility: float
    min_return: float
    max_return: float
    cumulative_return: float
