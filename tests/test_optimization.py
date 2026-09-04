"""
Unit tests for scenario simulator and PuLP decision optimizer.
"""

import pytest
from config.settings import settings
from src.data.loader import data_loader
from src.features.temporal import TemporalFeatureEngineer
from src.models.forecasting import ProductionForecaster
from src.optimization.scenario_simulator import ScenarioSimulator
from src.optimization.lp_solver import DecisionOptimizer


def test_scenario_simulator_and_decision_optimizer():
    forecaster = ProductionForecaster.load(settings.MODELS_DIR)
    simulator = ScenarioSimulator(forecaster)
    optimizer = DecisionOptimizer(simulator)
    
    prod_df = data_loader.load_production_data()
    block_a = prod_df[prod_df["mine_block_id"] == "BLOCK_A"].copy()
    feat_df = TemporalFeatureEngineer.create_features(block_a)
    
    rec_res = optimizer.generate_recommendations(
        base_features_df=feat_df,
        target_tonnes=10000.0,
        mine_block_id="BLOCK_A"
    )
    
    assert "options" in rec_res
    assert len(rec_res["options"]) >= 3
    
    # Check that rank 1 has highest net utility score
    scores = [opt["net_utility_score"] for opt in rec_res["options"]]
    assert scores == sorted(scores, reverse=True)
    
    # Check that recovery is positive
    for opt in rec_res["options"]:
        assert opt["expected_recovery_tonnes"] > 0
        assert opt["cost"] in ["Low", "Medium", "High"]
        assert opt["feasibility"] in ["Low", "Medium", "High"]
        
    assert rec_res["top_2_projected_recovery"] > 0
    assert rec_res["solver_status"] in ["Optimal", "Not Solved"]
