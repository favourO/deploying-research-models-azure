"""Strict parsing and validation for security-price CSV datasets."""

import csv
import io
import math
from datetime import date

from src.processing.exceptions import DatasetError
from src.processing.models import PriceObservation

REQUIRED_COLUMNS = {"ticker", "date", "price", "volume"}


def parse_price_csv(raw_csv: str) -> list[PriceObservation]:
    """Parse CSV without silently repairing invalid financial observations."""

    reader = csv.DictReader(io.StringIO(raw_csv))
    if reader.fieldnames is None:
        raise DatasetError("CSV input must include a header row.")
    if set(reader.fieldnames) != REQUIRED_COLUMNS:
        raise DatasetError("CSV columns must be exactly: ticker, date, price, volume.")

    observations: list[PriceObservation] = []
    seen: set[tuple[str, date]] = set()
    for row_number, row in enumerate(reader, start=2):
        if None in row or any(value is None for value in row.values()):
            raise DatasetError(
                f"Row {row_number}: column count does not match the CSV header."
            )
        ticker = (row.get("ticker") or "").strip()
        if not ticker:
            raise DatasetError(f"Row {row_number}: ticker must not be empty.")
        try:
            observation_date = date.fromisoformat(row["date"])
        except (TypeError, ValueError) as exc:
            raise DatasetError(
                f"Row {row_number}: date must use valid ISO format YYYY-MM-DD."
            ) from exc
        try:
            price = float(row["price"])
        except (TypeError, ValueError) as exc:
            raise DatasetError(f"Row {row_number}: price must be numeric.") from exc
        if not math.isfinite(price) or price <= 0:
            raise DatasetError(f"Row {row_number}: price must be positive and finite.")
        try:
            volume = int(row["volume"])
        except (TypeError, ValueError) as exc:
            raise DatasetError(f"Row {row_number}: volume must be an integer.") from exc
        if volume < 0:
            raise DatasetError(f"Row {row_number}: volume cannot be negative.")

        key = (ticker, observation_date)
        if key in seen:
            raise DatasetError(
                f"Row {row_number}: duplicate observation for {ticker} "
                f"on {observation_date.isoformat()}."
            )
        seen.add(key)
        observations.append(PriceObservation(ticker, observation_date, price, volume))

    if not observations:
        raise DatasetError("CSV input contains no observations.")
    return observations
