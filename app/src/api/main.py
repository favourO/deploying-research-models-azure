"""HTTP adapter for the research analysis application."""

from fastapi import FastAPI, HTTPException, status

from src.analysis import AnalysisError, calculate_summary_statistics
from src.api.models import AnalysisRequest, AnalysisResponse, HealthResponse

app = FastAPI(title="Research Analysis API", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="healthy")


@app.post("/analysis", response_model=AnalysisResponse)
def analyse(request: AnalysisRequest) -> AnalysisResponse:
    try:
        summary = calculate_summary_statistics(request.prices)
    except AnalysisError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The supplied price series cannot be analysed.",
        ) from exc

    return AnalysisResponse(
        ticker=request.ticker,
        observations=summary.observations,
        returns=list(summary.returns),
        mean_return=summary.mean_return,
        volatility=summary.volatility,
        min_return=summary.min_return,
        max_return=summary.max_return,
        cumulative_return=summary.cumulative_return,
    )
