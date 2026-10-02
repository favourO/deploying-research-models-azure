import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_web_interface() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Research return analyser" in response.text


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_valid_analysis_request() -> None:
    response = client.post(
        "/analysis",
        json={"ticker": "msft", "prices": [410.2, 415.8, 417.1, 430.5, 421.3]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "MSFT"
    assert body["observations"] == 5
    assert len(body["returns"]) == 4
    assert body["cumulative_return"] == pytest.approx(421.3 / 410.2 - 1)


@pytest.mark.parametrize(
    "payload",
    [
        {"ticker": "", "prices": [100, 101, 102]},
        {"ticker": "MSFT", "prices": [100, 101]},
        {"ticker": "MSFT", "prices": [100, 0, 102]},
        {"ticker": "MSFT", "prices": [100, -1, 102]},
    ],
)
def test_invalid_analysis_request(payload: dict[str, object]) -> None:
    response = client.post("/analysis", json=payload)
    assert response.status_code == 422
