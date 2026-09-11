"""
Comprehensive Test Suite for Phase 17: Decision Intelligence Integration & End-to-End Decision Workflow.
Validates the complete 9-stage decision chain:
DATA -> CONTEXT -> ANALYSIS -> EXPLANATION -> SCENARIO -> OPTIMIZATION -> RECOMMENDED ACTION -> LIMITATIONS
Verifies strict provenance classifications, non-causal SHAP language, scope isolation, and multi-mine behavior.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)

BANNED_TERMS = [
    "mineralization probability",
    "ore probability",
    "reserve probability",
    "ore likelihood",
    "confirmed ore zone",
    "mineralized zone",
    "calibrated mineralization probability",
    "model independently discovered the deposit"
]


class TestDecisionWorkflowPipeline:
    """Tests the unified GET /api/real/decision/{mine_id} endpoint across all 9 stages."""

    def test_balaghat_mine_decision_workflow_complete(self):
        res = client.get("/api/real/decision/MOIL_BALAGHAT")
        assert res.status_code == 200
        data = res.json()
        assert data["mine_id"] == "MOIL_BALAGHAT"
        assert "decision_workflow" in data

        dw = data["decision_workflow"]
        assert len(dw) == 9

        # Stage 1: Mine Context
        ctx = dw["stage_1_mine_context"]
        assert ctx["mine_id"] == "MOIL_BALAGHAT"
        assert ctx["district"] == "Balaghat"
        assert ctx["point_type"] == "shaft_portal"
        assert ctx["lease_area_ha"] == 180.44
        assert "REAL / SURVEYED" in ctx["data_classification"]

        # Stage 2: Data Status Breakdown
        status = dw["stage_2_data_status"]
        assert "AVAILABLE" in status["remote_sensing_rasters"]
        assert "AVAILABLE" in status["dsr_stratigraphy_context"]
        assert "AVAILABLE" in status["dsr_exploration_evidence"]
        assert "UNAVAILABLE" in status["cadastral_boundary_polygons"]

        # Stage 3: Observations and Features
        obs = dw["stage_3_observations_and_features"]
        assert "operational_baseline_inputs" in obs
        assert "geological_stratigraphy_reference" in obs
        strat = obs["geological_stratigraphy_reference"]
        assert len(strat["associated_formations"]) >= 1

        # Stage 4: Analytical Signal (Exploration + Production)
        signal = dw["stage_4_analytical_signal"]
        assert "exploration_analytical_signal" in signal
        exp_sig = signal["exploration_analytical_signal"]
        assert exp_sig["signal_type"] == "RELATIVE_EXPLORATION_PRIORITY_RANKING"
        assert exp_sig["data_classification"] == "EXPERIMENTAL"

        assert "production_forecast_signal" in signal
        prod_sig = signal["production_forecast_signal"]
        assert prod_sig["signal_type"] == "QUANTILE_PRODUCTION_FORECAST"
        assert prod_sig["horizon_days"] == 30
        assert prod_sig["baseline_forecast_tonnes"] > 0

        # Stage 5: Explanation (SHAP Non-Causal Attribution)
        exp = dw["stage_5_explanation"]
        assert exp["explanation_method"] == "Tree-SHAP (Shapley Additive Explanations)"
        assert len(exp["associated_contributors"]) >= 1
        for c in exp["associated_contributors"]:
            assert "associated with" in c["model_association"].lower()
            assert "caused" not in c["model_association"].lower()
            assert c["data_classification"] == "DERIVED_EXPLAINABILITY"

        # Stage 6: Scenario Workflow
        scen = dw["stage_6_scenario"]
        assert scen["scenario_status"] == "BASELINE_UNMODIFIED"
        assert scen["target_tonnes"] > 0

        # Stage 7: Optimization Workflow
        opt = dw["stage_7_optimization"]
        assert "PuLP" in opt["solver"]
        assert opt["solver_status"] in ("Optimal", "Feasible", "Not Solved")
        assert len(opt["selected_actions"]) >= 1

        # Stage 8: Recommended Action
        rec = dw["stage_8_recommended_action"]
        assert rec["decision_type"] == "INTEGRATED_MINE_DECISION_SUPPORT"
        assert "primary_recommended_action" in rec
        assert rec["primary_recommended_action"]["action_type"]
        assert len(rec["applicable_statutory_constraints"]) >= 1

        # Stage 9: Provenance and Limitations
        lim = dw["stage_9_provenance_and_limitations"]
        assert len(lim["what_tattva_knows"]) >= 4
        assert len(lim["what_tattva_derives"]) >= 3
        assert len(lim["what_tattva_simulates"]) >= 3
        assert len(lim["what_tattva_experimentally_ranks"]) >= 1
        assert len(lim["what_is_unavailable_and_not_claimed"]) >= 4

    def test_scenario_override_decision_workflow(self):
        """Tests that user-provided scenario adjustments propagate correctly through stages 4, 5, 6, 7."""
        res = client.get(
            "/api/real/decision/MOIL_BALAGHAT?horizon_days=45&custom_target=15000&equipment_availability_pct=92.0&rainfall_mm=25.0"
        )
        assert res.status_code == 200
        data = res.json()
        dw = data["decision_workflow"]

        scen = dw["stage_6_scenario"]
        assert scen["scenario_status"] == "SCENARIO_ADJUSTED"
        assert scen["target_tonnes"] == 15000.0
        assert scen["applied_overrides"]["equipment_availability_pct"] == 92.0
        assert scen["applied_overrides"]["rainfall_mm"] == 25.0

    def test_non_balaghat_mine_decision_workflow_isolation(self):
        """Tests that non-Balaghat mines handle regional raster / DSR unavailability gracefully."""
        res = client.get("/api/real/decision/MOIL_GUMGAON")
        assert res.status_code == 200
        data = res.json()
        assert data["mine_id"] == "MOIL_GUMGAON"

        dw = data["decision_workflow"]
        assert dw["stage_1_mine_context"]["district"] == "Nagpur"

        # Rasters and DSR stratigraphy must be marked unavailable
        status = dw["stage_2_data_status"]
        assert "UNAVAILABLE" in status["remote_sensing_rasters"]
        assert "UNAVAILABLE" in status["dsr_stratigraphy_context"]

        # Exploration analytical signal marked unavailable
        exp_sig = dw["stage_4_analytical_signal"]["exploration_analytical_signal"]
        assert "UNAVAILABLE" in exp_sig["status"]

        # Production forecast is strictly marked UNAVAILABLE_FOR_MINE for non-Balaghat mines
        prod_sig = dw["stage_4_analytical_signal"]["production_forecast_signal"]
        assert "UNAVAILABLE" in prod_sig["status"]

    def test_unknown_mine_decision_returns_404(self):
        res = client.get("/api/real/decision/UNKNOWN_MINE_XYZ")
        assert res.status_code == 404

    def test_no_banned_terms_in_decision_payload(self):
        """Verifies that no prohibited claims or terminology appear in decision API outputs."""
        for mine in ["MOIL_BALAGHAT", "MOIL_UKWA", "MOIL_TIRODI", "MOIL_GUMGAON"]:
            res = client.get(f"/api/real/decision/{mine}")
            assert res.status_code == 200
            content = res.text.lower()
            for term in BANNED_TERMS:
                assert term not in content, f"Prohibited term '{term}' found in decision payload for {mine}"
