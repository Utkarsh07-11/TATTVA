"""Pydantic schemas for the mining decision-support API."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    mine_block_id: str = Field(default="BLOCK_A")
    horizon_days: int = Field(default=30, ge=1, le=90)
    target_tonnes: Optional[float] = Field(default=None, ge=0.0)


class DailyForecastPoint(BaseModel):
    date: str
    p10: float
    p50: float
    p90: float


class ForecastResponse(BaseModel):
    mine_block_id: str
    forecast_tonnes: float
    interval_90: List[float]
    target_tonnes: float
    expected_shortfall_tonnes: float
    shortfall_pct: float
    shortfall_probability: float
    risk_level: str
    horizon_days: int
    daily_points: List[DailyForecastPoint]
    cv_metrics: Dict[str, Any] = Field(default_factory=dict)
    synthetic: bool = True


class ContributorItem(BaseModel):
    factor: str
    label: str
    contribution_pct: int
    raw_impact_tonnes: float


class ShortfallExplanationResponse(BaseModel):
    mine_block_id: str
    target_tonnes: float
    forecast_tonnes: float
    expected_shortfall: float
    contributors: List[ContributorItem]
    narrative: str
    note: str
    synthetic: bool = True


class RecommendationOption(BaseModel):
    rank: int
    action_id: str
    action: str
    title: str
    details: str
    category: str
    from_block: str
    to_block: str
    equipment_id: Optional[str] = None
    expected_recovery_tonnes: float
    cost: str
    feasibility: str
    net_utility_score: float
    lp_recommended: bool


class RecommendationResponse(BaseModel):
    mine_block_id: str
    target_tonnes: float
    baseline_forecast: float
    expected_shortfall: float
    top_2_projected_recovery: float
    residual_shortfall: float
    options: List[RecommendationOption]
    solver_status: str
    note: str
    synthetic: bool = True


class SimulationRequest(BaseModel):
    mine_block_id: str = Field(default="BLOCK_A")
    horizon_days: int = Field(default=30, ge=1, le=90)
    equipment_availability_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    blasting_delay_flag: Optional[int] = Field(default=None, ge=0, le=1)
    rainfall_mm: Optional[float] = Field(default=None, ge=0.0, le=300.0)


class SimulationResponse(BaseModel):
    mine_block_id: str
    baseline_tonnes: float
    simulated_tonnes: float
    expected_recovery_tonnes: float
    simulated_interval_90: List[float]
    applied_overrides: Dict[str, Any]
    synthetic: bool = True


class BlockSummary(BaseModel):
    block_id: str
    name: str
    status: str
    current_month_actual: float
    target_tonnes: float
    forecast_tonnes: float
    shortfall_probability: float
    risk_level: str


class MineOverviewResponse(BaseModel):
    mine_id: str
    mine_name: str
    selected_block: str
    total_monthly_target: float
    total_monthly_actual: float
    total_monthly_forecast: float
    aggregate_risk_level: str
    blocks: List[BlockSummary]
    active_equipment_count: int
    equipment_under_repair_count: int
    current_weather: Dict[str, Any]
    model_status: Dict[str, Any]
    synthetic_watermark: bool = True
