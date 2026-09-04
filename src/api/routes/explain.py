"""SHAP shortfall explanation endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from src.api.deps import block_feature_frame, get_forecaster, get_shap_engine, resolve_target
from src.api.schemas import ShortfallExplanationResponse, ContributorItem

router = APIRouter(prefix="/explain", tags=["Explainability (SHAP)"])


@router.get("/shortfall", response_model=ShortfallExplanationResponse)
def get_shortfall_explanation(
    mine_block_id: str = Query("BLOCK_A"),
    horizon_days: int = Query(30, ge=1, le=90),
    target_tonnes: Optional[float] = Query(None),
) -> ShortfallExplanationResponse:
    _, feat_df = block_feature_frame(mine_block_id)
    if feat_df is None or feat_df.empty:
        raise HTTPException(status_code=404, detail=f"Mine block '{mine_block_id}' not found or lacks features.")

    target = resolve_target(mine_block_id, target_tonnes, horizon_days)
    pred_res = get_forecaster().predict_horizon(feat_df, horizon_days=horizon_days)
    forecast = pred_res["forecast_tonnes"]
    shortfall = max(0.0, round(target - forecast, 1))

    explanation = get_shap_engine().explain_instance(
        feat_df.iloc[-1:],
        target_tonnes=target,
        forecast_tonnes=forecast,
    )

    contributor_items = [
        ContributorItem(
            factor=c["factor"],
            label=c["label"],
            contribution_pct=c["contribution_pct"],
            raw_impact_tonnes=c["raw_impact_tonnes"],
        )
        for c in explanation["contributors"]
    ]

    return ShortfallExplanationResponse(
        mine_block_id=mine_block_id,
        target_tonnes=target,
        forecast_tonnes=forecast,
        expected_shortfall=shortfall,
        contributors=contributor_items,
        narrative=explanation["narrative"],
        note=explanation["note"],
        synthetic=True,
    )
