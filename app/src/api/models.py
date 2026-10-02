"""Validated HTTP request and response schemas."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Ticker = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
PositivePrice = Annotated[float, Field(gt=0, allow_inf_nan=False)]


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: Ticker
    prices: list[PositivePrice] = Field(min_length=3)

    @field_validator("ticker")
    @classmethod
    def normalise_ticker(cls, ticker: str) -> str:
        return ticker.upper()


class AnalysisResponse(BaseModel):
    ticker: str
    observations: int
    returns: list[float]
    mean_return: float
    volatility: float
    min_return: float
    max_return: float
    cumulative_return: float


class HealthResponse(BaseModel):
    status: str
