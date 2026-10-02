"""Pure financial calculations with no transport or storage dependencies."""

import math
import statistics
from collections.abc import Sequence

from src.analysis.exceptions import (
    InsufficientObservationsError,
    InvalidPriceError,
)
from src.analysis.models import SummaryStatistics


def _validated_prices(prices: Sequence[float]) -> tuple[float, ...]:
    values = tuple(float(price) for price in prices)
    if len(values) < 2:
        raise InsufficientObservationsError(
            "At least two price observations are required."
        )
    if any(not math.isfinite(price) or price <= 0 for price in values):
        raise InvalidPriceError("Every price must be a positive, finite number.")
    return values


def calculate_returns(prices: Sequence[float]) -> tuple[float, ...]:
    """Calculate consecutive simple returns: P[t] / P[t-1] - 1."""

    values = _validated_prices(prices)
    return tuple(
        current / previous - 1
        for previous, current in zip(values, values[1:], strict=False)
    )


def calculate_mean_return(returns: Sequence[float]) -> float:
    """Calculate the arithmetic mean of a non-empty return series."""

    if not returns:
        raise InsufficientObservationsError("At least one return is required.")
    return statistics.fmean(returns)


def calculate_volatility(returns: Sequence[float]) -> float:
    """Calculate sample standard deviation (n-1) of historical returns."""

    if len(returns) < 2:
        raise InsufficientObservationsError(
            "At least two returns are required to calculate sample volatility."
        )
    return statistics.stdev(returns)


def calculate_cumulative_return(prices: Sequence[float]) -> float:
    """Calculate total simple return over an ordered price series."""

    values = _validated_prices(prices)
    return values[-1] / values[0] - 1


def calculate_summary_statistics(prices: Sequence[float]) -> SummaryStatistics:
    """Calculate all supported statistics for an ordered price series.

    Three prices are required because sample volatility needs two returns.
    """

    values = _validated_prices(prices)
    returns = calculate_returns(values)
    if len(returns) < 2:
        raise InsufficientObservationsError(
            "At least three prices are required for summary statistics."
        )
    return SummaryStatistics(
        observations=len(values),
        returns=returns,
        mean_return=calculate_mean_return(returns),
        volatility=calculate_volatility(returns),
        min_return=min(returns),
        max_return=max(returns),
        cumulative_return=calculate_cumulative_return(values),
    )
