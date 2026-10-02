import math
import statistics

import pytest

from src.analysis import (
    InsufficientObservationsError,
    InvalidPriceError,
    calculate_cumulative_return,
    calculate_mean_return,
    calculate_returns,
    calculate_summary_statistics,
    calculate_volatility,
)


def test_calculate_returns() -> None:
    assert calculate_returns([100.0, 110.0, 99.0]) == pytest.approx((0.1, -0.1))


def test_calculate_mean_return() -> None:
    assert calculate_mean_return([0.1, -0.05, 0.2]) == pytest.approx(1 / 12)


def test_calculate_volatility_uses_sample_standard_deviation() -> None:
    returns = [0.1, -0.05, 0.2]
    assert calculate_volatility(returns) == pytest.approx(statistics.stdev(returns))


def test_calculate_cumulative_return() -> None:
    assert calculate_cumulative_return([100.0, 110.0, 121.0]) == pytest.approx(0.21)


def test_summary_statistics() -> None:
    summary = calculate_summary_statistics([100.0, 110.0, 99.0])
    assert summary.observations == 3
    assert summary.returns == pytest.approx((0.1, -0.1))
    assert summary.mean_return == pytest.approx(0.0)
    assert summary.volatility == pytest.approx(math.sqrt(0.02))
    assert summary.min_return == pytest.approx(-0.1)
    assert summary.max_return == pytest.approx(0.1)
    assert summary.cumulative_return == pytest.approx(-0.01)


@pytest.mark.parametrize("prices", [[], [100.0]])
def test_returns_reject_insufficient_prices(prices: list[float]) -> None:
    with pytest.raises(InsufficientObservationsError, match="two price"):
        calculate_returns(prices)


def test_summary_rejects_one_return_for_sample_volatility() -> None:
    with pytest.raises(InsufficientObservationsError, match="three prices"):
        calculate_summary_statistics([100.0, 101.0])


@pytest.mark.parametrize("invalid_price", [0.0, -1.0, float("inf"), float("nan")])
def test_returns_reject_invalid_price(invalid_price: float) -> None:
    with pytest.raises(InvalidPriceError, match="positive, finite"):
        calculate_returns([100.0, invalid_price])


def test_mean_rejects_empty_returns() -> None:
    with pytest.raises(InsufficientObservationsError, match="one return"):
        calculate_mean_return([])


def test_volatility_rejects_one_return() -> None:
    with pytest.raises(InsufficientObservationsError, match="two returns"):
        calculate_volatility([0.1])
