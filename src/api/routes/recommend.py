"""Recommendation and what-if simulation endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from src.api.deps import block_feature_frame, get_optimizer, get_simulator, resolve_target
from src.api.schemas import (
    RecommendationResponse,
    RecommendationOption,
    SimulationRequest,
    SimulationResponse,
)

router = APIRouter(prefix="", tags=["Optimization & Decision Support"])


@router.get("/recommend/actions", response_model=RecommendationResponse)
def get_recommend_actions(
    mine_block_id: str = Query("BLOCK_A"),
    horizon_days: int = Query(30, ge=1, le=90),
    target_tonnes: Optional[float] = Query(None),
) -> RecommendationResponse:
    _, feat_df = block_feature_frame(mine_block_id)
    if feat_df is None or feat_df.empty:
        raise HTTPException(status_code=404, detail=f"Mine block '{mine_block_id}' not found.")

    target = resolve_target(mine_block_id, target_tonnes, horizon_days)
    res = get_optimizer().generate_recommendations(
        base_features_df=feat_df,
        target_tonnes=target,
        mine_block_id=mine_block_id,
        horizon_days=horizon_days,
    )

    options = [RecommendationOption(**opt) for opt in res["options"]]
    return RecommendationResponse(
        mine_block_id=mine_block_id,
        target_tonnes=target,
        baseline_forecast=res["baseline_forecast"],
        expected_shortfall=res["expected_shortfall"],
        top_2_projected_recovery=res["top_2_projected_recovery"],
        residual_shortfall=res["residual_shortfall"],
        options=options,
        solver_status=res["solver_status"],
        note=res["note"],
        synthetic=True,
    )


@router.post("/simulate/scenario", response_model=SimulationResponse)
def post_simulate_scenario(req: SimulationRequest) -> SimulationResponse:
    _, feat_df = block_feature_frame(req.mine_block_id)
    if feat_df is None or feat_df.empty:
        raise HTTPException(status_code=404, detail=f"Mine block '{req.mine_block_id}' not found.")

    overrides = {}
    if req.equipment_availability_pct is not None:
        overrides["equipment_availability_pct"] = req.equipment_availability_pct
    if req.blasting_delay_flag is not None:
        overrides["blasting_delay_flag"] = req.blasting_delay_flag
    if req.rainfall_mm is not None:
        overrides["rainfall_mm"] = req.rainfall_mm

    sim_res = get_simulator().simulate_action(
        base_features_df=feat_df,
        action_type="custom_slider",
        parameters=overrides,
        horizon_days=req.horizon_days,
    )

    return SimulationResponse(
        mine_block_id=req.mine_block_id,
        baseline_tonnes=sim_res["baseline_tonnes"],
        simulated_tonnes=sim_res["simulated_tonnes"],
        expected_recovery_tonnes=sim_res["expected_recovery_tonnes"],
        simulated_interval_90=sim_res["simulated_interval_90"],
        applied_overrides=sim_res["applied_overrides"],
        synthetic=True,
    )
