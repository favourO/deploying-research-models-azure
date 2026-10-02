"""Orchestration from validated observations to per-security results."""

from collections import defaultdict

from src.analysis import AnalysisError, calculate_summary_statistics
from src.processing.csv_parser import parse_price_csv
from src.processing.exceptions import DatasetError
from src.processing.models import PriceObservation, SecurityAnalysisResult


def analyse_observations(
    observations: list[PriceObservation],
) -> list[SecurityAnalysisResult]:
    grouped: dict[str, list[PriceObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.ticker].append(observation)

    results: list[SecurityAnalysisResult] = []
    for ticker in sorted(grouped):
        ordered = sorted(grouped[ticker], key=lambda item: item.date)
        try:
            summary = calculate_summary_statistics([item.price for item in ordered])
        except AnalysisError as exc:
            raise DatasetError(f"Ticker {ticker}: {exc}") from exc
        results.append(SecurityAnalysisResult(ticker=ticker, summary=summary))
    return results


def process_price_csv(raw_csv: str) -> list[SecurityAnalysisResult]:
    """Parse, validate, group, order, and analyse a price CSV document."""

    return analyse_observations(parse_price_csv(raw_csv))
