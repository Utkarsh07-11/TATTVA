"""Shared runtime: model loading, block metadata, and request-level caches."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Optional, Tuple

from config.settings import settings
from src.data.loader import data_loader
from src.explainability.shap_engine import ShapExplainerEngine
from src.features.temporal import TemporalFeatureEngineer
from src.models.forecasting import ProductionForecaster
from src.models.prospectivity import ProspectivityModel
from src.models.shortfall import ShortfallRiskEstimator
from src.optimization.lp_solver import DecisionOptimizer
from src.optimization.scenario_simulator import ScenarioSimulator

BLOCK_TARGETS: Dict[str, float] = {
    "BLOCK_A": 10000.0,
    "BLOCK_B": 8400.0,
    "BLOCK_C": 6600.0,
}

BLOCK_META = [
    {"id": "BLOCK_A", "name": "Main Pit — Block A (High Grade)", "target": 10000.0, "status": "Active Extraction"},
    {"id": "BLOCK_B", "name": "East Extension — Block B", "target": 8400.0, "status": "Active Extraction"},
    {"id": "BLOCK_C", "name": "South Overburden Strip — Block C", "target": 6600.0, "status": "Stripping"},
]


def resolve_target(mine_block_id: str, custom_target: Optional[float], horizon_days: int) -> float:
    monthly = BLOCK_TARGETS.get(mine_block_id, 10000.0)
    if custom_target is not None:
        return float(custom_target)
    return round((monthly / 30.0) * horizon_days, 1)


@lru_cache(maxsize=1)
def get_forecaster() -> ProductionForecaster:
    try:
        return ProductionForecaster.load(settings.MODELS_DIR)
    except Exception:
        prod_df = data_loader.load_production_data()
        forecaster = ProductionForecaster()
        forecaster.train_with_rolling_cv(prod_df, n_splits=3, test_window_days=30)
        forecaster.save(settings.MODELS_DIR)
        return forecaster


@lru_cache(maxsize=1)
def get_prospectivity_model() -> ProspectivityModel:
    model_path = settings.MODELS_DIR / "prospectivity_model.pkl"
    if model_path.exists():
        return ProspectivityModel.load(model_path)
    dh_df = data_loader.load_drillhole_assay()
    sat_df = data_loader.load_satellite_grid()
    model = ProspectivityModel()
    model.train_with_spatial_cv(dh_df, sat_df)
    model.save(model_path)
    return model


@lru_cache(maxsize=1)
def get_shap_engine() -> ShapExplainerEngine:
    forecaster = get_forecaster()
    return ShapExplainerEngine(forecaster.models[0.5], forecaster.feature_cols)


@lru_cache(maxsize=1)
def get_simulator() -> ScenarioSimulator:
    return ScenarioSimulator(get_forecaster())


@lru_cache(maxsize=1)
def get_optimizer() -> DecisionOptimizer:
    return DecisionOptimizer(get_simulator())


def block_feature_frame(mine_block_id: str):
    prod_df = data_loader.load_production_data()
    block_prod = prod_df[prod_df["mine_block_id"] == mine_block_id].copy()
    if block_prod.empty:
        return None, None
    return block_prod, TemporalFeatureEngineer.create_features(block_prod)


_forecast_cache: Dict[Tuple[str, int, float], Dict[str, Any]] = {}


def compute_forecast_payload(mine_block_id: str, horizon_days: int, custom_target: Optional[float] = None) -> Dict[str, Any]:
    target = resolve_target(mine_block_id, custom_target, horizon_days)
    cache_key = (mine_block_id, horizon_days, target)
    if cache_key in _forecast_cache:
        return _forecast_cache[cache_key]

    from datetime import timedelta
    from fastapi import HTTPException

    block_prod, feat_df = block_feature_frame(mine_block_id)
    if block_prod is None:
        raise HTTPException(status_code=404, detail=f"Mine block '{mine_block_id}' not found.")
    if feat_df is None or feat_df.empty:
        raise HTTPException(status_code=500, detail="Insufficient historical feature points for block.")

    forecaster = get_forecaster()
    pred_res = forecaster.predict_horizon(feat_df, horizon_days=horizon_days)
    risk_info = ShortfallRiskEstimator.evaluate_shortfall(
        forecast_tonnes=pred_res["forecast_tonnes"],
        interval_90=(pred_res["interval_90"][0], pred_res["interval_90"][1]),
        target_tonnes=target,
        mine_block_id=mine_block_id,
        horizon_days=horizon_days,
    )

    last_date = block_prod["date"].max()
    daily_points = []
    for day_idx in range(horizon_days):
        daily_points.append({
            "date": (last_date + timedelta(days=day_idx + 1)).strftime("%Y-%m-%d"),
            "p10": pred_res["daily_forecasts_10"][day_idx],
            "p50": pred_res["daily_forecasts_50"][day_idx],
            "p90": pred_res["daily_forecasts_90"][day_idx],
        })

    payload = {
        "mine_block_id": mine_block_id,
        "forecast_tonnes": pred_res["forecast_tonnes"],
        "interval_90": pred_res["interval_90"],
        "target_tonnes": target,
        "expected_shortfall_tonnes": risk_info["expected_shortfall_tonnes"],
        "shortfall_pct": risk_info["shortfall_pct"],
        "shortfall_probability": risk_info["shortfall_probability"],
        "risk_level": risk_info["risk_level"],
        "horizon_days": horizon_days,
        "daily_points": daily_points,
        "cv_metrics": forecaster.cv_metrics or {},
        "synthetic": True,
    }
    _forecast_cache[cache_key] = payload
    return payload


def runtime_status() -> Dict[str, Any]:
    issues = []
    models = {
        "forecasting": False,
        "prospectivity": False,
        "xai": False,
        "optimization": False,
    }
    try:
        models["forecasting"] = bool(get_forecaster().is_trained)
    except Exception as exc:
        issues.append(f"forecasting: {exc}")
    try:
        models["prospectivity"] = bool(get_prospectivity_model().is_trained)
    except Exception as exc:
        issues.append(f"prospectivity: {exc}")
    try:
        models["xai"] = get_shap_engine() is not None
    except Exception as exc:
        issues.append(f"xai: {exc}")
    try:
        models["optimization"] = get_optimizer() is not None
    except Exception as exc:
        issues.append(f"optimization: {exc}")

    prod_ok = (settings.PROCESSED_DATA_DIR / "production_daily.csv").exists() or (
        settings.SYNTHETIC_DATA_DIR / "production_daily.csv"
    ).exists()
    healthy = all(models.values()) and prod_ok and not issues
    return {
        "status": "healthy" if healthy else "degraded",
        "models_ready": models,
        "data_ready": prod_ok,
        "issues": issues,
        "crs": settings.CRS_PROJECTION,
        "synthetic_watermark": True,
    }
