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
    norm_id = mine_block_id.strip().upper()
    prod_df = data_loader.load_production_data()
    block_prod = prod_df[prod_df["mine_block_id"] == norm_id].copy()
    if block_prod.empty:
        return None, None
    return block_prod, TemporalFeatureEngineer.create_features(block_prod)


_forecast_cache: Dict[Tuple[str, int, float], Dict[str, Any]] = {}


def compute_forecast_payload(mine_block_id: str, horizon_days: int, custom_target: Optional[float] = None) -> Dict[str, Any]:
    norm_id = mine_block_id.strip().upper()
    target = resolve_target(norm_id, custom_target, horizon_days)
    cache_key = (norm_id, horizon_days, target)
    if cache_key in _forecast_cache:
        return _forecast_cache[cache_key]

    from datetime import timedelta
    from fastapi import HTTPException

    block_prod, feat_df = block_feature_frame(norm_id)
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
        mine_block_id=norm_id,
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
        "mine_block_id": norm_id,
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


def compute_production_reconciliation_payload(
    mine_block_id: str = "BLOCK_A",
    horizon_days: int = 30,
    custom_target: Optional[float] = None,
    equipment_availability_pct: Optional[float] = None,
    blasting_delay_flag: Optional[int] = None,
    rainfall_mm: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Computes Macro/Micro Production Intelligence and Operational Reconciliation.
    Strictly separates MOIL Company-Level Reported Production (Macro) from
    TATTVA Operational Simulation (Micro). Never allocates company totals to mines.
    """
    from fastapi import HTTPException
    norm_id = mine_block_id.strip().upper()
    
    # 1. Macro Context: Dynamic company-level reported historical series
    try:
        real_df = data_loader.load_real_production_df(period_type="annual", company="MOIL Limited")
        annual_records = []
        for _, r in real_df.iterrows():
            annual_records.append({
                "period": str(r["period"]),
                "production_tonnes": float(r["production_tonnes"]),
                "production_lakh_tonnes": round(float(r["production_tonnes"]) / 100000.0, 2),
                "source": str(r["source"]),
                "data_status": str(r["data_status"]),
            })
        
        latest_record = annual_records[-1] if annual_records else {}
        mean_tonnes = round(float(real_df["production_tonnes"].mean()), 1) if not real_df.empty else 0.0
        
        macro_context = {
            "status": "REPORTED DATA",
            "scope": "COMPANY_LEVEL_AGGREGATE",
            "company": "MOIL Limited",
            "commodity": "Manganese Ore",
            "series_count": len(annual_records),
            "period_range": f"{annual_records[0]['period']} to {annual_records[-1]['period']}" if annual_records else "N/A",
            "latest_reported_period": latest_record.get("period"),
            "latest_reported_tonnes": latest_record.get("production_tonnes"),
            "latest_reported_lakh_tonnes": latest_record.get("production_lakh_tonnes"),
            "historical_annual_mean_tonnes": mean_tonnes,
            "annual_series": annual_records,
            "scope_note": "MOIL reported production is company-level historical context. It is not allocated to individual mines or used as a mine-level historical target.",
            "source_citation": "MOIL Limited Statutory Annual Reports (FY16-FY24) & PIB Ministry of Steel Disclosures",
        }
    except Exception as e:
        macro_context = {
            "status": "REPORTED DATA",
            "scope": "COMPANY_LEVEL_AGGREGATE",
            "error": str(e),
            "scope_note": "MOIL reported production is company-level historical context. It is not allocated to individual mines or used as a mine-level historical target.",
        }

    # 2. Micro Baseline: TATTVA Operational Simulation for requested block
    base_forecast = compute_forecast_payload(
        mine_block_id=norm_id,
        horizon_days=horizon_days,
        custom_target=custom_target,
    )
    
    target_tonnes = float(base_forecast["target_tonnes"])
    baseline_forecast_tonnes = float(base_forecast["forecast_tonnes"])
    baseline_variance = round(baseline_forecast_tonnes - target_tonnes, 1)
    baseline_shortfall = max(0.0, round(target_tonnes - baseline_forecast_tonnes, 1))
    baseline_excess = max(0.0, round(baseline_forecast_tonnes - target_tonnes, 1))

    # 3. Scenario-Adjusted Simulation & Variance Layer
    has_scenario_overrides = any(
        p is not None for p in [equipment_availability_pct, blasting_delay_flag, rainfall_mm]
    )
    
    block_prod, feat_df = block_feature_frame(norm_id)
    if block_prod is None or feat_df is None or feat_df.empty:
        raise HTTPException(status_code=404, detail=f"Mine block '{mine_block_id}' not found.")

    scenario_params = {}
    if equipment_availability_pct is not None:
        scenario_params["equipment_availability_pct"] = float(equipment_availability_pct)
    if blasting_delay_flag is not None:
        scenario_params["blasting_delay_flag"] = int(blasting_delay_flag)
    if rainfall_mm is not None:
        scenario_params["rainfall_mm"] = float(rainfall_mm)

    if has_scenario_overrides:
        sim_engine = get_simulator()
        sim_res = sim_engine.simulate_action(
            feat_df,
            action_type="custom_slider",
            parameters=scenario_params,
            horizon_days=horizon_days,
        )
        scenario_tonnes = float(sim_res["simulated_tonnes"])
        scenario_interval = (float(sim_res["simulated_interval_90"][0]), float(sim_res["simulated_interval_90"][1]))
        expected_recovery = float(sim_res["expected_recovery_tonnes"])
        
        scenario_variance = round(scenario_tonnes - target_tonnes, 1)
        scenario_shortfall = max(0.0, round(target_tonnes - scenario_tonnes, 1))
        scenario_excess = max(0.0, round(scenario_tonnes - target_tonnes, 1))
        
        scenario_risk = ShortfallRiskEstimator.evaluate_shortfall(
            forecast_tonnes=scenario_tonnes,
            interval_90=scenario_interval,
            target_tonnes=target_tonnes,
            mine_block_id=norm_id,
            horizon_days=horizon_days,
        )
    else:
        scenario_tonnes = baseline_forecast_tonnes
        scenario_interval = (float(base_forecast["interval_90"][0]), float(base_forecast["interval_90"][1]))
        expected_recovery = 0.0
        scenario_variance = baseline_variance
        scenario_shortfall = baseline_shortfall
        scenario_excess = baseline_excess
        scenario_risk = {
            "expected_shortfall_tonnes": base_forecast["expected_shortfall_tonnes"],
            "shortfall_pct": base_forecast["shortfall_pct"],
            "shortfall_probability": base_forecast["shortfall_probability"],
            "risk_level": base_forecast["risk_level"],
        }

    # 4. Decision Optimizer Recommendations
    try:
        opt = get_optimizer()
        rec_data = opt.generate_recommendations(
            feat_df,
            target_tonnes=target_tonnes,
            mine_block_id=norm_id,
            horizon_days=horizon_days,
        )
        recommendations = rec_data.get("options", [])
    except Exception as e:
        recommendations = []

    # 5. Multi-Block Operational Target Context
    multi_block_summary = {
        "blocks": BLOCK_META,
        "total_monthly_target_tonnes": sum(b["target"] for b in BLOCK_META),
        "horizon_days": horizon_days,
        "active_block": norm_id,
    }

    return {
        "macro_context": macro_context,
        "micro_simulation": {
            "status": "SIMULATION",
            "scope": "BLOCK_OPERATIONAL",
            "mine_block_id": norm_id,
            "horizon_days": horizon_days,
            "operational_target_tonnes": target_tonnes,
            "baseline_forecast_tonnes": baseline_forecast_tonnes,
            "baseline_interval_90": base_forecast["interval_90"],
            "baseline_variance_tonnes": baseline_variance,
            "baseline_shortfall_tonnes": baseline_shortfall,
            "baseline_excess_tonnes": baseline_excess,
            "baseline_risk_level": base_forecast["risk_level"],
            "baseline_shortfall_probability": base_forecast["shortfall_probability"],
            "daily_points": base_forecast["daily_points"],
            "multi_block_targets": multi_block_summary,
        },
        "scenario_reconciliation": {
            "scope": "OPERATIONAL_TARGET_RECONCILIATION",
            "has_scenario_overrides": has_scenario_overrides,
            "applied_parameters": scenario_params,
            "operational_target_tonnes": target_tonnes,
            "simulated_output_tonnes": scenario_tonnes,
            "simulated_interval_90": scenario_interval,
            "expected_recovery_tonnes": expected_recovery,
            "scenario_variance_tonnes": scenario_variance,
            "scenario_shortfall_tonnes": scenario_shortfall,
            "scenario_excess_tonnes": scenario_excess,
            "scenario_risk_level": scenario_risk["risk_level"],
            "scenario_shortfall_probability": scenario_risk["shortfall_probability"],
        },
        "optimizer_recommendations": recommendations,
        "governance": {
            "macro_status": "REPORTED DATA",
            "micro_status": "TATTVA OPERATIONAL SIMULATION",
            "non_fabrication_policy": "Strict separation enforced: MOIL reported production is company-level historical context only. It is not allocated, inferred, or scaled to individual mines. TATTVA operational simulation represents synthetic block telemetry for decision-support modeling.",
            "scientific_disclaimer": "Relative ranking heuristic, not probability. No independent negative drillholes available.",
        },
    }


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
