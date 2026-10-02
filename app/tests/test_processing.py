import pytest

from src.processing import DatasetError, parse_price_csv, process_price_csv


def test_duplicate_ticker_date_is_rejected() -> None:
    raw = """ticker,date,price,volume
MSFT,2026-01-01,420.50,23000000
MSFT,2026-01-01,421.00,24000000
"""
    with pytest.raises(DatasetError, match="duplicate observation"):
        parse_price_csv(raw)


def test_unordered_input_is_ordered_before_analysis() -> None:
    raw = """ticker,date,price,volume
MSFT,2026-01-03,121,25
MSFT,2026-01-01,100,23
MSFT,2026-01-02,110,27
"""
    result = process_price_csv(raw)[0]
    assert result.summary.returns == pytest.approx((0.1, 0.1))
    assert result.summary.cumulative_return == pytest.approx(0.21)


def test_malformed_date_is_rejected() -> None:
    raw = "ticker,date,price,volume\nMSFT,not-a-date,100,20\n"
    with pytest.raises(DatasetError, match="valid ISO format"):
        parse_price_csv(raw)


def test_wrong_column_count_is_rejected() -> None:
    raw = "ticker,date,price,volume\nMSFT,2026-01-01,100,20,unexpected\n"
    with pytest.raises(DatasetError, match="column count"):
        parse_price_csv(raw)


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("price", "oops", "price must be numeric"),
        ("volume", "2.5", "volume must be an integer"),
    ],
)
def test_malformed_numbers_are_rejected(column: str, value: str, message: str) -> None:
    fields = {"ticker": "MSFT", "date": "2026-01-01", "price": "100", "volume": "20"}
    fields[column] = value
    raw = "ticker,date,price,volume\n{ticker},{date},{price},{volume}\n".format(
        **fields
    )
    with pytest.raises(DatasetError, match=message):
        parse_price_csv(raw)


def test_negative_volume_is_rejected() -> None:
    raw = "ticker,date,price,volume\nMSFT,2026-01-01,100,-1\n"
    with pytest.raises(DatasetError, match="cannot be negative"):
        parse_price_csv(raw)


def test_empty_ticker_is_rejected() -> None:
    raw = "ticker,date,price,volume\n,2026-01-01,100,1\n"
    with pytest.raises(DatasetError, match="ticker must not be empty"):
        parse_price_csv(raw)


def test_multiple_tickers_are_grouped_and_analysed() -> None:
    raw = """ticker,date,price,volume
MSFT,2026-01-01,100,10
AAPL,2026-01-01,50,20
MSFT,2026-01-02,110,11
AAPL,2026-01-02,55,21
MSFT,2026-01-03,121,12
AAPL,2026-01-03,60.5,22
"""
    results = process_price_csv(raw)
    assert [result.ticker for result in results] == ["AAPL", "MSFT"]
    assert all(
        result.summary.returns == pytest.approx((0.1, 0.1)) for result in results
    )


def test_ticker_with_insufficient_observations_fails_clearly() -> None:
    raw = "ticker,date,price,volume\nMSFT,2026-01-01,100,10\n"
    with pytest.raises(DatasetError, match="Ticker MSFT: At least two"):
        process_price_csv(raw)
