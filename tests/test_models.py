"""
Unit tests for ML models: Prospectivity, Quantile Forecasting, and Shortfall.
"""

import pytest
import pandas as pd
from config.settings import settings
from src.data.loader import data_loader
from src.features.temporal import TemporalFeatureEngineer
from src.models.forecasting import ProductionForecaster
from src.models.shortfall import ShortfallRiskEstimator
from src.models.prospectivity import ProspectivityModel


def test_production_forecaster_quantiles():
    forecaster = ProductionForecaster.load(settings.MODELS_DIR)
    assert forecaster.is_trained
    
    prod_df = data_loader.load_production_data()
    block_a = prod_df[prod_df["mine_block_id"] == "BLOCK_A"].copy()
    feat_df = TemporalFeatureEngineer.create_features(block_a)
    
    res = forecaster.predict_horizon(feat_df, horizon_days=30)
    assert "forecast_tonnes" in res
    assert "interval_90" in res
    p10, p90 = res["interval_90"]
    p50 = res["forecast_tonnes"]
    
    # Quantile monotonicity check
    assert p10 <= p50, f"p10 ({p10}) should be <= p50 ({p50})"
    assert p50 <= p90, f"p50 ({p50}) should be <= p90 ({p90})"
    assert len(res["daily_forecasts_50"]) == 30


def test_shortfall_risk_estimator():
    # Test High Shortfall case
    high_risk = ShortfallRiskEstimator.evaluate_shortfall(
        forecast_tonnes=8650.0,
        interval_90=(7900.0, 9300.0),
        target_tonnes=10000.0,
        mine_block_id="BLOCK_A"
    )
    assert high_risk["expected_shortfall_tonnes"] == 1350.0
    assert high_risk["shortfall_probability"] >= 0.70
    assert high_risk["risk_level"] in ["HIGH", "CRITICAL"]
    
    # Test Low Shortfall case
    low_risk = ShortfallRiskEstimator.evaluate_shortfall(
        forecast_tonnes=10500.0,
        interval_90=(9800.0, 11200.0),
        target_tonnes=10000.0,
        mine_block_id="BLOCK_A"
    )
    assert low_risk["expected_shortfall_tonnes"] == 0.0
    assert low_risk["shortfall_probability"] < 0.35
    assert low_risk["risk_level"] == "LOW"


def test_prospectivity_model_predictions():
    model = ProspectivityModel.load(settings.MODELS_DIR / "prospectivity_model.pkl")
    assert model.is_trained
    
    sat_df = data_loader.load_satellite_grid()
    scored = model.predict_grid_surface(sat_df)
    
    assert "prospectivity_prob" in scored.columns
    assert scored["prospectivity_prob"].min() >= 0.0
    assert scored["prospectivity_prob"].max() <= 1.0
    assert "uncertainty" in scored.columns
    
    geojson = model.to_geojson_feature_collection(scored)
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == len(sat_df)
