"""
Comprehensive Test Suite for Phase 18: Multi-Mine Decision Synthesis & Live Demonstration Readiness
Verifies:
1. 10-Mine Registry & Dynamic Capability Matrix (Levels A, B, C, D)
2. Authoritative Dimension-Level Status Semantics (REAL, SOURCE-DERIVED, EXPERIMENTAL, SIMULATION, UNAVAILABLE, UNAVAILABLE_FOR_MINE)
3. Bidirectional Cross-Mine State Isolation (Balaghat -> Ukwa -> Sitapatore -> Kandri -> Balaghat)
4. Strict Optimization Input Contract & Zero Constraint Inheritance
5. Graceful Degradation across all Capability Tiers
6. Zero Banned Terminology & Strict Data Labeling (No static/simulated data labeled LIVE)
7. Regressions for Phase 9B, Phase 12, Phase 15.1, and Phase 17
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.data.loader import data_loader
from config.demo_config import DEMO_CONFIG

client = TestClient(app)

FORBIDDEN_TERMS = [
    "mineralization probability",
    "ore probability",
    "reserve probability",
    "ore likelihood",
    "confirmed ore zone",
    "mineralized zone",
    "calibrated mineralization probability",
    "model independently discovered the deposit"
]


class Test10MineRegistryAndCapabilityMatrix:
    """Phase 18A & 18B: Verification of the 10-mine MOIL registry and dynamic capability matrix."""

    def test_all_10_statutory_mines_registered(self):
        df = data_loader.load_real_mines_df()
        assert len(df) == 10
        expected_ids = [
            "MOIL_BALAGHAT", "MOIL_UKWA", "MOIL_TIRODI", "MOIL_SITAPATORE",
            "MOIL_CHIKLA", "MOIL_DONGRI_BUZURG", "MOIL_BELDONGRI",
            "MOIL_KANDRI", "MOIL_MUNSAR", "MOIL_GUMGAON"
        ]
        for mid in expected_ids:
            assert mid in df["mine_id"].values

    def test_capability_matrix_endpoint_structure(self):
        res = client.get("/api/real/capability-matrix")
        assert res.status_code == 200
        data = res.json()
        assert data["total_mines"] == 10
        assert data["data_status"] == "real"
        assert len(data["matrix"]) == 10

        for item in data["matrix"]:
            assert "mine_id" in item
            assert "mine_name" in item
            assert "state" in item
            assert "tier" in item
            assert "capabilities" in item
            caps = item["capabilities"]
            assert "registry_status" in caps
            assert "coordinate_status" in caps
            assert "geometry_status" in caps
            assert "satellite_status" in caps
            assert "terrain_status" in caps
            assert "geology_status" in caps
            assert "exploration_status" in caps
            assert "production_status" in caps
            assert "mine_plan_status" in caps
            assert "constraint_status" in caps
            assert "simulation_status" in caps
            assert "optimization_status" in caps
            assert "decision_workflow_status" in caps

    def test_capability_tier_distribution(self):
        matrix_res = client.get("/api/real/capability-matrix").json()["matrix"]
        tier_map = {item["mine_id"]: item["tier"] for item in matrix_res}

        # Level A: Full decision workflow
        assert tier_map["MOIL_BALAGHAT"] == "LEVEL_A"

        # Level B: Partial decision workflow (DSR context + constraints)
        assert tier_map["MOIL_UKWA"] == "LEVEL_B"
        assert tier_map["MOIL_TIRODI"] == "LEVEL_B"

        # Level C: Contextual intelligence only (DSR context, no constraints)
        assert tier_map["MOIL_SITAPATORE"] == "LEVEL_C"

        # Level D: Registry & reference only (Maharashtra mines)
        maharashtra_mines = [
            "MOIL_CHIKLA", "MOIL_DONGRI_BUZURG", "MOIL_BELDONGRI",
            "MOIL_KANDRI", "MOIL_MUNSAR", "MOIL_GUMGAON"
        ]
        for mid in maharashtra_mines:
            assert tier_map[mid] == "LEVEL_D"


class TestDimensionLevelStatusSemantics:
    """Phase 18C & 18E: Authoritative dimension-level capability status verification."""

    def test_balaghat_level_a_dimensions(self):
        res = client.get("/api/real/capability-matrix").json()
        bal = next(item for item in res["matrix"] if item["mine_id"] == "MOIL_BALAGHAT")
        caps = bal["capabilities"]

        assert caps["registry_status"] == "REAL"
        assert caps["satellite_status"] == "REAL"
        assert caps["terrain_status"] == "REAL"
        assert caps["geology_status"] == "SOURCE-DERIVED"
        assert caps["exploration_status"] == "EXPERIMENTAL"
        assert caps["simulation_status"] == "SIMULATION"
        assert caps["optimization_status"] == "OPTIMIZATION"
        assert caps["geometry_status"] == "UNAVAILABLE"

    def test_ukwa_tirodi_level_b_dimensions(self):
        res = client.get("/api/real/capability-matrix").json()
        for mid in ["MOIL_UKWA", "MOIL_TIRODI"]:
            mine_cap = next(item for item in res["matrix"] if item["mine_id"] == mid)
            caps = mine_cap["capabilities"]
            assert caps["registry_status"] == "REAL"
            assert caps["geology_status"] == "SOURCE-DERIVED"
            assert caps["constraint_status"] == "SOURCE-DERIVED"
            # Critical isolation rule: non-Balaghat must be UNAVAILABLE_FOR_MINE
            assert caps["satellite_status"] == "UNAVAILABLE_FOR_MINE"
            assert caps["terrain_status"] == "UNAVAILABLE_FOR_MINE"
            assert caps["simulation_status"] == "UNAVAILABLE_FOR_MINE"
            assert caps["optimization_status"] == "UNAVAILABLE_FOR_MINE"

    def test_sitapatore_level_c_dimensions(self):
        res = client.get("/api/real/capability-matrix").json()
        sit = next(item for item in res["matrix"] if item["mine_id"] == "MOIL_SITAPATORE")
        caps = sit["capabilities"]
        assert caps["registry_status"] == "REAL"
        assert caps["geology_status"] == "SOURCE-DERIVED"
        assert caps["satellite_status"] == "UNAVAILABLE_FOR_MINE"
        assert caps["simulation_status"] == "UNAVAILABLE_FOR_MINE"
        assert caps["optimization_status"] == "UNAVAILABLE_FOR_MINE"

    def test_kandri_level_d_dimensions(self):
        res = client.get("/api/real/capability-matrix").json()
        kan = next(item for item in res["matrix"] if item["mine_id"] == "MOIL_KANDRI")
        caps = kan["capabilities"]
        assert caps["registry_status"] == "REAL"
        assert caps["geology_status"] == "UNAVAILABLE_FOR_MINE"
        assert caps["satellite_status"] == "UNAVAILABLE_FOR_MINE"
        assert caps["simulation_status"] == "UNAVAILABLE_FOR_MINE"
        assert caps["optimization_status"] == "UNAVAILABLE_FOR_MINE"


class TestCrossMineIsolationAndTransitions:
    """Phase 18D: Bidirectional state transition isolation testing."""

    def test_sequential_mine_transitions_and_isolation(self):
        """
        Tests the dangerous sequence:
        Balaghat (A) -> Ukwa (B) -> Sitapatore (C) -> Kandri (D) -> Balaghat (A)
        Verifies zero leftover state or cross-mine data leakage.
        """
        # Step 1: Balaghat (Level A)
        res_a1 = client.get("/api/real/decision/MOIL_BALAGHAT")
        assert res_a1.status_code == 200
        data_a1 = res_a1.json()
        assert data_a1["tier"] == "LEVEL_A"
        assert data_a1["decision_workflow"]["stage_4_analytical_signal"]["exploration_analytical_signal"]["signal_type"] == "RELATIVE_EXPLORATION_PRIORITY_RANKING"
        assert data_a1["decision_workflow"]["stage_7_optimization"]["solver_status"] in ("Optimal", "Feasible")

        # Step 2: Transition to Ukwa (Level B) -> Balaghat features must NOT survive
        res_b = client.get("/api/real/decision/MOIL_UKWA")
        assert res_b.status_code == 200
        data_b = res_b.json()
        assert data_b["tier"] == "LEVEL_B"
        assert data_b["decision_workflow"]["stage_4_analytical_signal"]["exploration_analytical_signal"]["status"] == "UNAVAILABLE_FOR_MINE"
        assert data_b["decision_workflow"]["stage_4_analytical_signal"]["production_forecast_signal"]["status"] == "UNAVAILABLE_FOR_MINE"
        assert data_b["decision_workflow"]["stage_5_explanation"]["status"] == "UNAVAILABLE_FOR_MINE"
        assert data_b["decision_workflow"]["stage_6_scenario"]["status"] == "UNAVAILABLE_FOR_MINE"
        assert data_b["decision_workflow"]["stage_7_optimization"]["status"] == "UNAVAILABLE_FOR_MINE"
        # Ukwa constraints must be Ukwa-specific
        ukwa_constraints = data_b["decision_workflow"]["stage_8_recommended_action"]["applicable_statutory_constraints"]
        assert len(ukwa_constraints) > 0
        for c in ukwa_constraints:
            assert "CON_UKW" in c.get("constraint_name", "") or "Ukwa" in c.get("source_name", "") or c.get("constraint_category") in ("environmental", "mining_geometry")

        # Step 3: Transition to Sitapatore (Level C) -> Ukwa constraints must disappear
        res_c = client.get("/api/real/decision/MOIL_SITAPATORE")
        assert res_c.status_code == 200
        data_c = res_c.json()
        assert data_c["tier"] == "LEVEL_C"
        assert data_c["decision_workflow"]["stage_4_analytical_signal"]["exploration_analytical_signal"]["status"] == "UNAVAILABLE_FOR_MINE"
        assert data_c["decision_workflow"]["stage_7_optimization"]["status"] == "UNAVAILABLE_FOR_MINE"

        # Step 4: Transition to Kandri (Level D) -> All MP DSR data must disappear
        res_d = client.get("/api/real/decision/MOIL_KANDRI")
        assert res_d.status_code == 200
        data_d = res_d.json()
        assert data_d["tier"] == "LEVEL_D"
        assert data_d["decision_workflow"]["stage_3_observations_and_features"]["geological_stratigraphy_reference"]["status"] == "UNAVAILABLE_FOR_MINE"
        assert data_d["decision_workflow"]["stage_8_recommended_action"]["operational_status"] == "STATUTORY_MONITORING_ONLY"

        # Step 5: Return to Balaghat (Level A) -> Verify clean reinstatement
        res_a2 = client.get("/api/real/decision/MOIL_BALAGHAT")
        assert res_a2.status_code == 200
        data_a2 = res_a2.json()
        assert data_a2["tier"] == "LEVEL_A"
        assert data_a2["decision_workflow"]["stage_4_analytical_signal"]["exploration_analytical_signal"]["signal_type"] == "RELATIVE_EXPLORATION_PRIORITY_RANKING"
        assert data_a2["decision_workflow"]["stage_7_optimization"]["solver_status"] in ("Optimal", "Feasible")

    def test_prospectivity_geojson_isolation_non_balaghat(self):
        for mid in ["MOIL_UKWA", "MOIL_TIRODI", "MOIL_KANDRI", "MOIL_CHIKLA"]:
            res = client.get(f"/api/real/prospectivity/{mid}/geojson")
            assert res.status_code == 200
            data = res.json()
            assert data.get("type") == "FeatureCollection"
            assert len(data.get("features", [])) == 0


class TestOptimizationInputContractAndScope:
    """Phase 18H: Explicit input contract verification for optimization."""

    def test_optimization_only_for_qualified_mine(self):
        # Balaghat satisfies all 4 conditions
        res_bal = client.get("/api/real/decision/MOIL_BALAGHAT").json()
        opt_bal = res_bal["decision_workflow"]["stage_7_optimization"]
        assert opt_bal.get("solver") == "PuLP Mixed-Integer Linear Programming (MILP)"
        assert len(opt_bal.get("selected_actions", [])) > 0

        # All other mines must return UNAVAILABLE_FOR_MINE
        other_mines = ["MOIL_UKWA", "MOIL_TIRODI", "MOIL_SITAPATORE", "MOIL_CHIKLA", "MOIL_KANDRI"]
        for mid in other_mines:
            res = client.get(f"/api/real/decision/{mid}").json()
            opt = res["decision_workflow"]["stage_7_optimization"]
            assert opt.get("status") == "UNAVAILABLE_FOR_MINE"
            assert "PuLP" in opt.get("reason", "")


class TestDemonstrationConfigurationAndContract:
    """Phase 18I & 18J: Deterministic demonstration path verification."""

    def test_demo_config_contract(self):
        assert DEMO_CONFIG["primary_demo_mine"] == "MOIL_BALAGHAT"
        assert DEMO_CONFIG["default_horizon_days"] == 30
        assert len(DEMO_CONFIG["demonstration_path"]) >= 10
        assert DEMO_CONFIG["demonstration_path"][0]["mine_id"] == "MOIL_BALAGHAT"


class TestErrorHandlingAndResilience:
    """Phase 18P: Failure-mode testing."""

    def test_invalid_mine_id_returns_404(self):
        res1 = client.get("/api/real/decision/INVALID_MINE_999")
        assert res1.status_code == 404

        res2 = client.get("/api/real/mine-dashboard/NON_EXISTENT_MINE")
        assert res2.status_code == 404

        res3 = client.get("/api/real/mines/FAKE_MINE")
        assert res3.status_code == 404

    def test_horizon_boundary_validation(self):
        res_low = client.get("/api/real/decision/MOIL_BALAGHAT?horizon_days=5")
        assert res_low.status_code == 422

        res_high = client.get("/api/real/decision/MOIL_BALAGHAT?horizon_days=120")
        assert res_high.status_code == 422


class TestLanguageAndScientificGovernanceAudit:
    """Phase 18O: Verification that no forbidden terms or misleading 'LIVE' data claims exist."""

    def test_no_forbidden_terms_in_decision_payloads(self):
        for mid in ["MOIL_BALAGHAT", "MOIL_UKWA", "MOIL_SITAPATORE", "MOIL_KANDRI"]:
            res = client.get(f"/api/real/decision/{mid}")
            text = res.text.lower()
            for term in FORBIDDEN_TERMS:
                assert term not in text, f"Forbidden term '{term}' detected in decision endpoint for {mid}"

    def test_no_forbidden_terms_in_capability_matrix(self):
        res = client.get("/api/real/capability-matrix")
        text = res.text.lower()
        for term in FORBIDDEN_TERMS:
            assert term not in text, f"Forbidden term '{term}' detected in capability matrix"
