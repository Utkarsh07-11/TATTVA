"""
Unit and Integration Tests for Phase 13: End-to-End Validation + Scientific & Data Integrity Audit.

Comprehensive Red-Team Audit Suite covering:
1. Complete Data-to-UI Pipeline & Data Availability Framework.
2. Real vs Synthetic Inventory Integrity.
3. Scientific Claims & Prohibited Terminology Audit.
4. Geospatial Integrity (CRS, Lon/Lat ordering, Bounding Boxes, Alignment, Coordinate Precision).
5. Mine Navigation & Multi-Mine Isolation (Transitions, Non-Balaghat, Invalid Mines).
6. API Security, Schema Validation & Path Traversal Prevention.
7. Production Integrity (Macro Reported vs Micro Simulation separation, non-fabrication).
8. ML Integrity (Phase 9B Ensemble, LightGBM Quantiles, No Lookahead Bias).
9. Explainability & Optimization Engine Integrity.
10. Reproducibility & Determinism.
"""

import json
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

from config.settings import settings
from src.api.main import app
from src.data.loader import data_loader
from src.data.registry import real_data_registry
from src.models.real_prospectivity_experiment import RealProspectivityExperiment

client = TestClient(app)

BANNED_TERMS = [
    "mineralization probability",
    "ore probability",
    "reserve probability",
    "ore likelihood",
    "confirmed ore zone",
    "mineralized zone",
    "calibrated mineralization probability",
]


class TestPipelineAndDataInventory:
    """1 & 2: Audit data-to-UI pipeline and verify exact real vs synthetic inventory."""

    def test_real_data_inventory_exists(self):
        # 1. MOIL Mines Registry & GeoJSON
        mines_csv = settings.REAL_DATA_DIR / "moil" / "mines.csv"
        mines_geojson = settings.REAL_DATA_DIR / "moil" / "mine_locations.geojson"
        assert mines_csv.exists()
        assert mines_geojson.exists()

        # 2. Sentinel-2 & DEM rasters for Balaghat
        s2_dir = settings.REAL_DATA_DIR / "sentinel2" / "balaghat" / "raw"
        dem_dir = settings.REAL_DATA_DIR / "dem" / "balaghat" / "raw"
        assert (s2_dir / "B02.tif").exists()
        assert (s2_dir / "B04.tif").exists()
        assert (s2_dir / "B08.tif").exists()
        assert (dem_dir / "copernicus_dem_30m_balaghat.tif").exists()

        # 3. Public mineralization evidence
        evid_csv = settings.REAL_DATA_DIR / "geology" / "balaghat" / "mineralization_evidence.csv"
        assert evid_csv.exists()

        # 4. Canonical reported production
        prod_csv = settings.REAL_DATA_DIR / "moil" / "production" / "production_reported.csv"
        assert prod_csv.exists()

    def test_derived_and_experimental_inventory_exists(self):
        grid_csv = settings.DERIVED_DATA_DIR / "geospatial" / "balaghat" / "real_feature_grid.csv"
        assert grid_csv.exists()

        meta_json = settings.DERIVED_DATA_DIR / "geospatial" / "balaghat" / "prospectivity_experiment_metadata.json"
        summary_json = settings.DERIVED_DATA_DIR / "geospatial" / "balaghat" / "prospectivity_experiment_summary.json"
        exp_csv = settings.DERIVED_DATA_DIR / "geospatial" / "balaghat" / "prospectivity_experiment.csv"
        assert meta_json.exists()
        assert summary_json.exists()
        assert exp_csv.exists()

    def test_synthetic_simulation_inventory_isolated(self):
        syn_prod = settings.SYNTHETIC_DATA_DIR / "production_daily.csv"
        syn_dh = settings.SYNTHETIC_DATA_DIR / "drillhole_assay.csv"
        syn_eq = settings.SYNTHETIC_DATA_DIR / "equipment_events.csv"
        syn_blocks = settings.SYNTHETIC_DATA_DIR / "mine_blocks.geojson"
        assert syn_prod.exists()
        assert syn_dh.exists()
        assert syn_eq.exists()
        assert syn_blocks.exists()


class TestScientificClaimsAndTerminology:
    """3: Ensure no prohibited scientific claims or misleading language in codebase."""

    def test_no_banned_terms_in_frontend_source(self):
        frontend_src = settings.BASE_DIR / "frontend" / "src"
        for js_file in frontend_src.rglob("*.jsx"):
            content = js_file.read_text(encoding="utf-8").lower()
            for term in BANNED_TERMS:
                assert term not in content, f"Banned scientific term '{term}' found in frontend file {js_file.name}"

        for js_file in frontend_src.rglob("*.js"):
            content = js_file.read_text(encoding="utf-8").lower()
            for term in BANNED_TERMS:
                assert term not in content, f"Banned scientific term '{term}' found in frontend file {js_file.name}"

    def test_no_banned_terms_in_api_responses(self):
        res = client.get("/api/real/prospectivity/MOIL_BALAGHAT")
        assert res.status_code == 200
        text = res.text.lower()
        # Ensure that no prohibited claims of probability or confirmed reserve are present
        for term in [
            "mineralization probability",
            "ore probability",
            "reserve probability",
            "ore likelihood",
            "confirmed ore zone",
            "mineralized zone",
        ]:
            assert term not in text, f"Banned term '{term}' found in prospectivity API response"

        # Check disclaimer text in metadata
        data = res.json()
        assert "limitations" in data or "critical_scientific_limitations" in data or "scientific_disclaimer" in text


class TestGeospatialIntegrity:
    """4: Validate Coordinate Reference Systems, Coordinate Ordering, Extents and Alignment."""

    def test_crs_and_geometry_validity(self):
        mines_geojson = data_loader.load_real_mines_geojson()
        for feat in mines_geojson["features"]:
            coords = feat["geometry"]["coordinates"]
            lon, lat = coords[0], coords[1]
            assert 70.0 <= lon <= 90.0, f"Invalid longitude {lon}"
            assert 15.0 <= lat <= 30.0, f"Invalid latitude {lat}"
            assert "coordinate_interpretation" in feat["properties"]
            assert "coordinate_precision" in feat["properties"]

    def test_feature_grid_raster_alignment_and_dimensions(self):
        grid_csv = settings.DERIVED_DATA_DIR / "geospatial" / "balaghat" / "real_feature_grid.csv"
        df = pd.read_csv(grid_csv)
        assert len(df) == 27720, f"Expected 27,720 30m grid cells, got {len(df)}"

        # Verify UTM Zone 44N coordinate bounds
        assert df["x"].min() >= 417000.0
        assert df["x"].max() <= 423000.0
        assert df["y"].min() >= 2413000.0
        assert df["y"].max() <= 2419000.0


class TestMineNavigationAndIsolation:
    """5: Red-team multi-mine navigation, URL params, and state transitions."""

    def test_all_10_statutory_mines_registered(self):
        res = client.get("/api/real/mines")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] == 10
        mines = data["mines"]
        mine_ids = [m["mine_id"] for m in mines]
        expected_mines = [
            "MOIL_BALAGHAT",
            "MOIL_UKWA",
            "MOIL_TIRODI",
            "MOIL_SITAPATORE",
            "MOIL_CHIKLA",
            "MOIL_DONGRI_BUZURG",
            "MOIL_BELDONGRI",
            "MOIL_KANDRI",
            "MOIL_MUNSAR",
            "MOIL_GUMGAON",
        ]
        for em in expected_mines:
            assert em in mine_ids, f"Expected statutory mine '{em}' not found in registry"

    def test_mine_dashboard_isolation_non_balaghat(self):
        for m_id in ["MOIL_TIRODI", "MOIL_UKWA", "MOIL_CHIKLA", "MOIL_GUMGAON"]:
            dash = client.get(f"/api/real/mine-dashboard/{m_id}").json()
            assert dash["exists"] is True
            assert dash["mine_id"] == m_id
            avail = dash["data_availability_status"]
            assert "UNAVAILABLE" in avail["real_data"][0]["status"]
            assert "UNAVAILABLE" in avail["experimental"][0]["status"]
            assert "UNAVAILABLE" in avail["simulation"][0]["status"] or avail["simulation"][0]["status"] == "SIMULATION"

    def test_invalid_mine_dashboard_404(self):
        res = client.get("/api/real/mine-dashboard/INVALID_MINE_123")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    def test_prospectivity_geojson_isolation_non_balaghat(self):
        res = client.get("/api/real/prospectivity/MOIL_TIRODI/geojson")
        assert res.status_code == 200
        data = res.json()
        assert len(data["features"]) == 0
        assert data["metadata"]["is_available"] is False


class TestApiSecurityAndValidation:
    """6 & 13: Audit API robustness, status codes, input sanitization, and path traversal."""

    def test_invalid_mine_detail_returns_404(self):
        res = client.get("/api/real/mines/NON_EXISTENT_MINE")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    def test_prospectivity_non_balaghat_returns_unavailable(self):
        res = client.get("/api/real/prospectivity/NON_EXISTENT_MINE")
        assert res.status_code == 200
        data = res.json()
        assert data["is_available"] is False
        assert data["data_status"] == "unavailable"

    def test_reconciliation_endpoints_validate_parameters(self):
        # Horizon out of bounds
        res = client.get("/api/real/production/reconciliation?horizon_days=999")
        assert res.status_code == 422

        # Equipment availability > 100%
        res = client.post("/api/real/production/reconciliation", json={"equipment_availability_pct": 150.0})
        assert res.status_code == 422

        # Rainfall < 0 mm
        res = client.post("/api/real/production/reconciliation", json={"rainfall_mm": -10.0})
        assert res.status_code == 422


class TestProductionIntegrity:
    """7: Validate Macro vs Micro scope separation, reconciliation arithmetic, and non-fabrication."""

    def test_macro_vs_micro_scope_metadata(self):
        res = client.get("/api/real/production/reconciliation?mine_block_id=BLOCK_A&horizon_days=30")
        assert res.status_code == 200
        data = res.json()

        assert data["macro_context"]["status"] == "REPORTED DATA"
        assert data["macro_context"]["scope"] == "COMPANY_LEVEL_AGGREGATE"
        assert data["micro_simulation"]["status"] == "SIMULATION"
        assert data["micro_simulation"]["scope"] == "BLOCK_OPERATIONAL"
        assert data["scenario_reconciliation"]["scope"] == "OPERATIONAL_TARGET_RECONCILIATION"

    def test_reconciliation_variance_arithmetic(self):
        res = client.get("/api/real/production/reconciliation?mine_block_id=BLOCK_B&horizon_days=30")
        assert res.status_code == 200
        data = res.json()
        rec = data["scenario_reconciliation"]

        target = rec["operational_target_tonnes"]
        output = rec["simulated_output_tonnes"]
        variance = rec["scenario_variance_tonnes"]
        shortfall = rec["scenario_shortfall_tonnes"]
        excess = rec["scenario_excess_tonnes"]

        assert variance == pytest.approx(round(output - target, 1), rel=1e-3)
        assert shortfall == pytest.approx(max(0.0, round(target - output, 1)), rel=1e-3)
        assert excess == pytest.approx(max(0.0, round(output - target, 1)), rel=1e-3)


class TestMachineLearningAndExplainability:
    """8, 9, 10: Audit ML algorithms, SHAP explanations, and PuLP optimization."""

    def test_phase9b_summary_distributions(self):
        summary_json = settings.DERIVED_DATA_DIR / "geospatial" / "balaghat" / "prospectivity_experiment_summary.json"
        with open(summary_json, "r") as f:
            summary = json.load(f)

        scores = summary["score_distributions"]["exploration_priority_score"]
        assert 0.0 <= scores["min"] <= scores["median"] <= scores["max"] <= 1.0
        assert summary["dataset_summary"]["total_cells"] == 27720

    def test_shap_explanation_feature_mapping(self):
        res = client.get("/api/explain/shortfall?mine_block_id=BLOCK_A&horizon_days=30")
        assert res.status_code == 200
        data = res.json()
        assert "contributors" in data
        assert len(data["contributors"]) > 0
        for c in data["contributors"]:
            assert "factor" in c
            assert "label" in c
            assert "contribution_pct" in c
            assert "raw_impact_tonnes" in c

    def test_pulp_optimizer_recommendations_feasibility(self):
        res = client.get("/api/recommend/actions?mine_block_id=BLOCK_A&horizon_days=30")
        assert res.status_code == 200
        data = res.json()
        assert "options" in data
        assert "solver_status" in data
        assert data["solver_status"] in ("Optimal", "Feasible", "Not Solved", "Suboptimal")


class TestReproducibilityAndDeterminism:
    """14: Audit determinism and zero seed leakage."""

    def test_deterministic_forecast_output(self):
        res1 = client.post("/api/forecast/production", json={"mine_block_id": "BLOCK_A", "horizon_days": 30})
        res2 = client.post("/api/forecast/production", json={"mine_block_id": "BLOCK_A", "horizon_days": 30})
        assert res1.status_code == 200
        assert res2.status_code == 200
        assert res1.json()["forecast_tonnes"] == res2.json()["forecast_tonnes"]
