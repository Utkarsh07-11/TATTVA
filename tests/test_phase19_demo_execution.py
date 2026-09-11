"""
Phase 19: Comprehensive Automated Test Suite for Live Demonstration Execution & Pitch Packaging.
Verifies:
1. Single Authoritative Demo Configuration Contract (12 steps, 300s timing, notes, disclosures).
2. Hierarchical 6-Category Pre-Flight Health Engine (DATA, CAPABILITY, ISOLATION, DECISION, FRONTEND, PERFORMANCE).
3. Public Application Pathway Parity (Zero demo shortcuts or mock bypasses).
4. Deterministic 12-Step Replay & Reset Behavior.
5. Strict Multi-Mine Isolation & UNAVAILABLE_FOR_MINE Semantic Enforcement.
6. Scientific Governance & Zero Forbidden Terminology in Pitch Scripts.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from config.demo_config import DEMO_CONFIG

client = TestClient(app)

FORBIDDEN_TERMS = [
    "mineralization probability",
    "ore probability",
    "reserve probability",
    "ore likelihood",
    "confirmed ore zone",
    "calibrated mineralization probability",
    "model independently discovered the deposit"
]


class TestAuthoritativeDemoConfigContract:
    """Verifies that config/demo_config.py is the single authoritative source of truth."""

    def test_demo_config_metadata(self):
        assert DEMO_CONFIG["version"] == "2.0.0"
        assert DEMO_CONFIG["primary_demo_mine"] == "MOIL_BALAGHAT"
        assert DEMO_CONFIG["total_presentation_time_sec"] == 300
        assert DEMO_CONFIG["default_horizon_days"] == 30

    def test_demo_path_12_steps_contract(self):
        path = DEMO_CONFIG["demonstration_path"]
        assert len(path) == 12, "Demonstration path must have exactly 12 steps"

        expected_mines = [
            "MOIL_BALAGHAT",  # Step 1
            "MOIL_BALAGHAT",  # Step 2
            "MOIL_BALAGHAT",  # Step 3
            "MOIL_BALAGHAT",  # Step 4
            "MOIL_BALAGHAT",  # Step 5
            "MOIL_BALAGHAT",  # Step 6
            "MOIL_BALAGHAT",  # Step 7
            "MOIL_BALAGHAT",  # Step 8
            "MOIL_UKWA",      # Step 9
            "MOIL_SITAPATORE",# Step 10
            "MOIL_KANDRI",    # Step 11
            "MOIL_BALAGHAT",  # Step 12
        ]

        expected_tiers = [
            "LEVEL_A", "LEVEL_A", "LEVEL_A", "LEVEL_A",
            "LEVEL_A", "LEVEL_A", "LEVEL_A", "LEVEL_A",
            "LEVEL_B", "LEVEL_C", "LEVEL_D", "LEVEL_A"
        ]

        for i, step in enumerate(path):
            assert step["step_id"] == i + 1
            assert step["mine_id"] == expected_mines[i]
            assert step["tier"] == expected_tiers[i]
            assert "title" in step and len(step["title"]) > 0
            assert "target_screen" in step
            assert "action_type" in step
            assert "timing_target_sec" in step and step["timing_target_sec"] > 0
            assert "speaker_notes" in step and len(step["speaker_notes"]) > 10
            assert "juror_defense_notes" in step and len(step["juror_defense_notes"]) > 10
            assert "governance_disclosure" in step and len(step["governance_disclosure"]) > 10
            assert "expected_capability" in step
            assert "expected_api_response" in step


class TestPreflightHealthHierarchy:
    """Verifies the hierarchical 6-category preflight endpoint."""

    def test_preflight_endpoint_structure_and_categories(self):
        res = client.get("/api/real/demo/preflight")
        assert res.status_code == 200
        data = res.json()

        assert data["status"] == "PASS"
        assert "timestamp" in data
        assert "categories" in data
        assert "performance" in data

        cats = data["categories"]
        assert "data" in cats
        assert "capability" in cats
        assert "isolation" in cats
        assert "decision_workflow" in cats
        assert "frontend" in cats

        # Data Category
        assert cats["data"]["status"] == "PASS"
        assert cats["data"]["checks"]["files_readable"] == "PASS"
        assert cats["data"]["checks"]["schemas_valid"] == "PASS"
        assert cats["data"]["checks"]["provenance_valid"] == "PASS"

        # Capability Category
        assert cats["capability"]["status"] == "PASS"
        assert cats["capability"]["checks"]["capability_matrix_valid"] == "PASS"
        assert cats["capability"]["checks"]["mine_specific_availability_correct"] == "PASS"
        assert cats["capability"]["checks"]["unavailable_states_enforced"] == "PASS"

        # Isolation Category
        assert cats["isolation"]["status"] == "PASS"
        assert cats["isolation"]["checks"]["no_balaghat_forecast_leakage"] == "PASS"
        assert cats["isolation"]["checks"]["no_balaghat_shap_leakage"] == "PASS"
        assert cats["isolation"]["checks"]["no_balaghat_exploration_leakage"] == "PASS"
        assert cats["isolation"]["checks"]["no_balaghat_optimization_leakage"] == "PASS"

        # Decision Workflow Category
        assert cats["decision_workflow"]["status"] == "PASS"
        assert cats["decision_workflow"]["checks"]["context_stage"] == "PASS"
        assert cats["decision_workflow"]["checks"]["analysis_stage"] == "PASS"
        assert cats["decision_workflow"]["checks"]["explanation_stage"] == "PASS"
        assert cats["decision_workflow"]["checks"]["scenario_stage"] == "PASS"
        assert cats["decision_workflow"]["checks"]["optimization_stage"] == "PASS"
        assert cats["decision_workflow"]["checks"]["recommendation_stage"] == "PASS"

        # Frontend Category
        assert cats["frontend"]["status"] == "PASS"
        assert cats["frontend"]["checks"]["backend_reachable"] == "PASS"

    def test_preflight_performance_telemetry(self):
        res = client.get("/api/real/demo/preflight")
        assert res.status_code == 200
        perf = res.json()["performance"]

        assert perf["target_ms"] == 100.0
        assert "observed_ms" in perf and perf["observed_ms"] > 0
        assert "within_target" in perf and isinstance(perf["within_target"], bool)
        assert perf["benchmark_method"] == "median_warm_cache_5_iterations"
        assert len(perf["sample_runs_ms"]) == 5


class TestDemoStepEndpointsAndParity:
    """Verifies step querying and 404 boundary conditions."""

    def test_all_12_step_endpoints(self):
        for step_id in range(1, 13):
            res = client.get(f"/api/real/demo/step/{step_id}")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "success"
            assert data["step"]["step_id"] == step_id
            assert data["total_steps"] == 12

    def test_invalid_step_id_returns_404(self):
        for invalid_id in [0, 13, 99, -1]:
            res = client.get(f"/api/real/demo/step/{invalid_id}")
            assert res.status_code == 404


class TestDeterministic12StepExecutionAndPublicParity:
    """Simulates full 12-step execution using standard public application routes."""

    def test_step_1_overview_public_pathway(self):
        res = client.get("/api/real/mines")
        assert res.status_code == 200
        data = res.json()
        assert len(data.get("mines", [])) == 10

    def test_step_2_remote_sensing_public_pathway(self):
        res = client.get("/api/real/mines/MOIL_BALAGHAT/layers")
        assert res.status_code == 200
        layers = res.json().get("layers", {})
        assert layers.get("sentinel2_true_color") is True
        assert layers.get("elevation") is True

    def test_step_3_exploration_priority_public_pathway(self):
        res = client.get("/api/real/prospectivity/MOIL_BALAGHAT/geojson")
        assert res.status_code == 200
        data = res.json()
        assert len(data.get("features", [])) == 27720

    def test_step_4_dsr_geology_public_pathway(self):
        res = client.get("/api/real/dsr/MOIL_BALAGHAT/geology")
        assert res.status_code == 200
        data = res.json()
        assert data.get("formation_count", 0) > 0 or len(data.get("regional_stratigraphy", [])) > 0

    def test_step_5_production_forecast_public_pathway(self):
        res = client.get("/api/real/decision/MOIL_BALAGHAT")
        assert res.status_code == 200
        dw = res.json()["decision_workflow"]
        assert "LightGBM" in dw["stage_4_analytical_signal"]["production_forecast_signal"]["model"]
        assert "Tree-SHAP" in dw["stage_5_explanation"]["explanation_method"]

    def test_step_6_scenario_sandbox_public_pathway(self):
        res = client.post(
            "/api/real/production/reconciliation",
            json={
                "mine_block_id": "BLOCK_A",
                "horizon_days": 30,
                "equipment_availability_pct": 88.0,
                "blasting_delay_flag": 0,
                "rainfall_mm": 12.5,
                "custom_target": 10000.0
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert "scenario_reconciliation" in data
        assert data["scenario_reconciliation"]["has_scenario_overrides"] is True

    def test_step_7_optimization_milp_public_pathway(self):
        res = client.get("/api/real/decision/MOIL_BALAGHAT")
        assert res.status_code == 200
        opt = res.json()["decision_workflow"]["stage_7_optimization"]
        assert opt["solver"] == "PuLP Mixed-Integer Linear Programming (MILP)"
        assert opt["solver_status"] in ("Optimal", "Feasible")

    def test_step_8_provenance_audit_public_pathway(self):
        res = client.get("/api/real/decision/MOIL_BALAGHAT")
        assert res.status_code == 200
        prov = res.json()["decision_workflow"]["stage_9_provenance_and_limitations"]
        assert len(prov["data_classification_taxonomy"]) == 9

    def test_step_9_ukwa_level_b_degradation_public_pathway(self):
        res = client.get("/api/real/decision/MOIL_UKWA")
        assert res.status_code == 200
        data = res.json()
        assert data["tier"] == "LEVEL_B"
        dw = data["decision_workflow"]
        assert dw["stage_4_analytical_signal"]["exploration_analytical_signal"]["status"] == "UNAVAILABLE_FOR_MINE"
        assert dw["stage_4_analytical_signal"]["production_forecast_signal"]["status"] == "UNAVAILABLE_FOR_MINE"
        assert dw["stage_7_optimization"]["status"] == "UNAVAILABLE_FOR_MINE"

    def test_step_10_sitapatore_level_c_degradation_public_pathway(self):
        res = client.get("/api/real/decision/MOIL_SITAPATORE")
        assert res.status_code == 200
        data = res.json()
        assert data["tier"] == "LEVEL_C"
        dw = data["decision_workflow"]
        assert dw["stage_7_optimization"]["status"] == "UNAVAILABLE_FOR_MINE"

    def test_step_11_kandri_level_d_degradation_public_pathway(self):
        res = client.get("/api/real/decision/MOIL_KANDRI")
        assert res.status_code == 200
        data = res.json()
        assert data["tier"] == "LEVEL_D"
        dw = data["decision_workflow"]
        assert dw["stage_3_observations_and_features"]["geological_stratigraphy_reference"]["status"] == "UNAVAILABLE_FOR_MINE"

    def test_step_12_balaghat_reinstatement_public_pathway(self):
        res = client.get("/api/real/decision/MOIL_BALAGHAT")
        assert res.status_code == 200
        data = res.json()
        assert data["tier"] == "LEVEL_A"
        assert data["decision_workflow"]["stage_7_optimization"]["solver_status"] in ("Optimal", "Feasible")


class TestLanguageAndScientificGovernanceInDemoScript:
    """Verifies that demo scripts and teleprompter texts contain zero prohibited terms."""

    def test_zero_forbidden_terms_in_demo_config(self):
        for step in DEMO_CONFIG["demonstration_path"]:
            text_corpus = f"{step['speaker_notes']} {step['juror_defense_notes']} {step['governance_disclosure']}".lower()
            for term in FORBIDDEN_TERMS:
                assert term not in text_corpus, (
                    f"Forbidden term '{term}' detected in Step {step['step_id']} text corpus!"
                )
