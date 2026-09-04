"""Production forecasting endpoints."""

from typing import Optional
from fastapi import APIRouter, Query

from src.api.deps import compute_forecast_payload
from src.api.schemas import ForecastRequest, ForecastResponse

router = APIRouter(prefix="/forecast", tags=["Production Forecasting"])


@router.post("/production", response_model=ForecastResponse)
def post_forecast_production(request: ForecastRequest) -> ForecastResponse:
    payload = compute_forecast_payload(
        mine_block_id=request.mine_block_id,
        horizon_days=request.horizon_days,
        custom_target=request.target_tonnes,
    )
    return ForecastResponse(**payload)


@router.get("/production", response_model=ForecastResponse)
def get_forecast_production(
    mine_block_id: str = Query("BLOCK_A"),
    horizon_days: int = Query(30, ge=1, le=90),
    target_tonnes: Optional[float] = Query(None),
) -> ForecastResponse:
    payload = compute_forecast_payload(
        mine_block_id=mine_block_id,
        horizon_days=horizon_days,
        custom_target=target_tonnes,
    )
    return ForecastResponse(**payload)
