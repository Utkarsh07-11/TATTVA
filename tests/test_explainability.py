"""
Unit tests for SHAP explainability and operational attribution.
"""

import pytest
from config.settings import settings
from src.data.loader import data_loader
from src.features.temporal import TemporalFeatureEngineer
from src.models.forecasting import ProductionForecaster
from src.explainability.shap_engine import ShapExplainerEngine


def test_shap_explainability_attribution():
    forecaster = ProductionForecaster.load(settings.MODELS_DIR)
    p50_model = forecaster.models[0.5]
    explainer = ShapExplainerEngine(p50_model, forecaster.feature_cols)
    
    prod_df = data_loader.load_production_data()
    block_a = prod_df[prod_df["mine_block_id"] == "BLOCK_A"].copy()
    feat_df = TemporalFeatureEngineer.create_features(block_a)
    
    res = explainer.explain_instance(feat_df.iloc[-1:], target_tonnes=10000.0, forecast_tonnes=8650.0)
    assert "contributors" in res
    assert len(res["contributors"]) > 0
    
    # Check that percentages sum to 100%
    total_pct = sum(c["contribution_pct"] for c in res["contributors"])
    assert total_pct == 100
    
    # Verify attribution disclaimer note
    assert "not verified physical causation" in res["note"]
    assert "narrative" in res and len(res["narrative"]) > 20
