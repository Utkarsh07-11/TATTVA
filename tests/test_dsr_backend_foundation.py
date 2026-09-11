"""
Comprehensive Test Suite for Phase 15.1: TATTVA Data Provenance + Lease Geometry Correction Audit.
Validates strict provenance taxonomy, statutory survey & reference points, unavailable polygon geometry handling,
projected metric CRS area calculations, area discrepancy reconciliations, and REST API endpoints.
"""

import json
import pytest
import pandas as pd
from fastapi.testclient import TestClient

from config.settings import settings
from src.data.loader import data_loader
from src.data.registry import real_data_registry
from src.data.validator import DataValidator, VALID_PROVENANCE_CATEGORIES, VALID_POINT_TYPES
from src.api.main import app

client = TestClient(app)


class TestDsrDataFilesAndProvenance:
    """Verifies that all DSR 2022 dataset files exist and contain valid provenance tags."""

    def test_dsr_source_manifest_exists_and_valid(self):
        manifest_file = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "source_manifest.json"
        assert manifest_file.exists(), f"DSR manifest not found at {manifest_file}"

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["district"] == "Balaghat"
        assert manifest["state"] == "Madhya Pradesh"
        assert manifest["publication_year"] == 2022
        assert len(manifest["sources"]) >= 4
        assert len(manifest["datasets"]) >= 10

        for ds in manifest["datasets"]:
            assert ds["data_status"] in ("source-derived", "real")
            assert ds["provenance_status"] in ("verified", "partial")
            assert ds["file"]
            if "provenance_category" in ds:
                assert ds["provenance_category"] in VALID_PROVENANCE_CATEGORIES

    def test_dsr_readme_exists(self):
        readme_file = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "README.md"
        assert readme_file.exists()
        content = readme_file.read_text(encoding="utf-8")
        assert "Balaghat District Survey Report" in content
        assert "Phase 15.1" in content

    def test_dsr_registry_descriptors_in_real_data_registry(self):
        descriptors = real_data_registry.list_descriptors()
        dsr_ids = {d.dataset_id for d in descriptors if "dsr" in d.dataset_id}
        expected_ids = {
            "dsr_balaghat_manifest", "dsr_balaghat_mines", "dsr_balaghat_lease_areas",
            "dsr_balaghat_boundary_pillars", "dsr_balaghat_boundaries_geojson",
            "dsr_balaghat_geology", "dsr_balaghat_grade", "dsr_balaghat_exploration",
            "dsr_balaghat_production", "dsr_balaghat_mine_plan", "dsr_balaghat_constraints"
        }
        assert expected_ids.issubset(dsr_ids)

        for d in descriptors:
            if "dsr" in d.dataset_id:
                assert d.is_available, f"Dataset {d.dataset_id} file missing on disk: {d.path}"
                assert d.data_status == "source-derived"


class TestDsrDataLoadingAndValidation:
    """Verifies DataLoader methods and DataValidator rules for all DSR datasets."""

    def test_dsr_mine_registry_loading_and_point_types(self):
        df = data_loader.load_dsr_mine_registry()
        valid, errors = DataValidator.validate_dsr_mine_registry(df)
        assert valid, f"DSR mine registry validation failed: {errors}"

        assert len(df) >= 6
        expected_mines = {"MOIL_BALAGHAT", "MOIL_UKWA", "MOIL_TIRODI", "MOIL_SITAPATORE"}
        assert expected_mines.issubset(set(df["mine_id"]))

        assert df["point_type"].isin(VALID_POINT_TYPES).all()
        assert df["provenance_category"].isin(VALID_PROVENANCE_CATEGORIES).all()

        # Bharweli shaft check
        bal_df = data_loader.load_dsr_mine_registry(mine_id="MOIL_BALAGHAT")
        assert len(bal_df) == 1
        assert bal_df.iloc[0]["mine_id"] == "MOIL_BALAGHAT"
        assert bal_df.iloc[0]["point_type"] == "shaft_portal"
        assert bal_df.iloc[0]["provenance_category"] == "REAL / SURVEYED"

    def test_augmented_moil_mines_registry_compatibility(self):
        df = data_loader.load_real_mines_df()
        assert "point_type" in df.columns
        assert "tehsil" in df.columns
        assert "lease_area_ha" in df.columns
        assert len(df) == 10
        assert (df["data_status"] == "real").all()

    def test_dsr_lease_areas_loading_and_reconciliation(self):
        df = data_loader.load_dsr_lease_areas()
        valid, errors = DataValidator.validate_dsr_lease_areas(df)
        assert valid, f"Lease areas validation failed: {errors}"

        assert len(df) >= 6
        assert "forest_area_ha" in df.columns
        assert "non_forest_area_ha" in df.columns
        assert "total_lease_area_ha" in df.columns
        assert "area_discrepancy_notes" in df.columns
        assert (df["total_lease_area_ha"] > 0).all()

        # Bharweli lease check
        b_df = data_loader.load_dsr_lease_areas(mine_id="MOIL_BALAGHAT")
        assert len(b_df) == 1
        assert b_df.iloc[0]["total_lease_area_ha"] == 180.44
        assert b_df.iloc[0]["forest_area_ha"] == 38.20
        assert b_df.iloc[0]["non_forest_area_ha"] == 142.24

        # Ukwa lease area reconciliation check
        u_df = data_loader.load_dsr_lease_areas(mine_id="MOIL_UKWA")
        assert len(u_df) == 1
        ukw_row = u_df.iloc[0]
        assert ukw_row["total_lease_area_ha"] == 199.07
        assert ukw_row["consolidated_lease_area_ha"] == 247.63
        assert ukw_row["historical_application_area_ha"] == 272.634
        assert "reconciled" in str(ukw_row["area_discrepancy_notes"]).lower()

    def test_dsr_boundary_pillars_validation_and_provenance(self):
        df = data_loader.load_dsr_boundary_pillars()
        valid, errors = DataValidator.validate_dsr_boundary_pillars(df)
        assert valid, f"Boundary pillars validation failed: {errors}"

        assert len(df) >= 6
        assert "latitude" in df.columns
        assert "longitude" in df.columns
        assert "utm_easting" in df.columns
        assert "utm_northing" in df.columns
        assert "provenance_category" in df.columns
        assert "point_type" in df.columns

        # Verify all coordinates have valid provenance categories
        assert df["provenance_category"].isin(VALID_PROVENANCE_CATEGORIES).all()
        assert df["point_type"].isin(VALID_POINT_TYPES).all()

        # Verify Bharweli shaft portal point
        bal_pts = data_loader.load_dsr_boundary_pillars(mine_id="MOIL_BALAGHAT")
        shaft_pt = bal_pts[bal_pts["point_type"] == "shaft_portal"].iloc[0]
        assert shaft_pt["latitude"] == 21.8464
        assert shaft_pt["longitude"] == 80.2281
        assert shaft_pt["provenance_category"] == "REAL / SURVEYED"

    def test_dsr_boundaries_geojson_points_and_unavailable_polygons(self):
        geojson = data_loader.load_dsr_boundaries_geojson()
        valid, errors = DataValidator.validate_dsr_boundaries_geojson(geojson)
        assert valid, f"Boundaries GeoJSON validation failed: {errors}"

        metadata = geojson.get("metadata", {})
        assert metadata.get("polygon_geometry_status") == "unavailable"
        assert metadata.get("point_geometry_status") == "available"

        features = geojson["features"]
        assert len(features) >= 6

        # Verify all features are Point geometries with explicit provenance
        for f in features:
            assert f["geometry"]["type"] == "Point"
            coords = f["geometry"]["coordinates"]
            assert len(coords) == 2
            props = f["properties"]
            assert props["polygon_geometry_status"] == "unavailable"
            assert props["point_type"] in VALID_POINT_TYPES
            assert props["provenance_category"] in VALID_PROVENANCE_CATEGORIES

    def test_projected_crs_polygon_area_calculation(self):
        """Tests the metric projected CRS area calculation function on a known test square."""
        # 1 km x 1 km square near Bharweli (100 Ha = 1,000,000 m2)
        # In UTM Zone 44N, 1000m x 1000m = 100 Ha
        test_wgs84_coords = [
            [80.2200, 21.8400],
            [80.2297, 21.8400],
            [80.2297, 21.8490],
            [80.2200, 21.8490],
            [80.2200, 21.8400]
        ]
        calc_ha = DataValidator.calculate_projected_polygon_area_ha(test_wgs84_coords)
        assert calc_ha > 90.0 and calc_ha < 110.0, f"Expected ~100 Ha, got {calc_ha:.2f} Ha"

    def test_dsr_geology_reference_stratigraphy(self):
        df = data_loader.load_dsr_geology_reference()
        valid, errors = DataValidator.validate_dsr_geology_reference(df)
        assert valid, f"Geology reference validation failed: {errors}"

        formations = set(df["formation_name"])
        expected_formations = {
            "Bichua Formation", "Junewani Formation", "Chorbaoli Formation",
            "Mansar Formation", "Lohangi Formation", "Sitasaongi Formation",
            "Tirodi Biotite Gneiss"
        }
        assert expected_formations.issubset(formations)

        mansar = df[df["formation_name"] == "Mansar Formation"].iloc[0]
        assert "Braunite" in mansar["primary_minerals"]
        assert "MOIL_BALAGHAT" in mansar["representative_mines"]

    def test_dsr_grade_reference_distributions(self):
        df = data_loader.load_dsr_grade_reference()
        valid, errors = DataValidator.validate_dsr_grade_reference(df)
        assert valid, f"Grade reference validation failed: {errors}"

        assert len(df) >= 8
        assert (df["mn_typical_pct"] >= 25.0).all()
        assert (df["mn_typical_pct"] <= 50.0).all()
        assert (df["fe_typical_pct"] > 0.0).all()
        assert (df["sio2_typical_pct"] > 0.0).all()
        assert (df["p_typical_pct"] > 0.0).all()

    def test_dsr_exploration_evidence_separation_from_collars(self):
        df = data_loader.load_dsr_exploration_evidence()
        assert len(df) >= 5
        assert "boreholes_drilled" in df.columns
        assert "total_meterage_m" in df.columns
        assert "unfc_reserves_111_mt" in df.columns
        assert (df["boreholes_drilled"] > 0).all()
        assert (df["total_meterage_m"] > 0).all()
        assert (df["data_status"] == "source-derived").all()

    def test_dsr_production_and_plan_targets_strict_separation(self):
        prod_df = data_loader.load_dsr_production_reference()
        plan_df = data_loader.load_dsr_mine_plan_targets()

        valid_p, errors_p = DataValidator.validate_dsr_production_reference(prod_df)
        assert valid_p, f"Production reference validation failed: {errors_p}"

        # Production statuses must only be reported_actual or reported_aggregate
        assert prod_df["production_status"].isin({"reported_actual", "reported_aggregate"}).all()

        # Plan targets must be planned
        assert (plan_df["plan_status"] == "planned").all()

        # Ensure no planned targets accidentally present in production_reference
        assert "planned" not in set(prod_df["production_status"])

    def test_dsr_constraints_validation(self):
        df = data_loader.load_dsr_constraints()
        valid, errors = DataValidator.validate_dsr_constraints(df)
        assert valid, f"Constraints validation failed: {errors}"
        assert len(df) >= 8
        assert "constraint_category" in df.columns
        assert "value" in df.columns
        assert "unit" in df.columns


class TestDsrApiEndpoints:
    """Verifies FastAPI REST endpoints under /api/real/dsr/*."""

    def test_get_dsr_manifest(self):
        res = client.get("/api/real/dsr")
        assert res.status_code == 200
        data = res.json()
        assert data["district"] == "Balaghat"
        assert len(data["sources"]) >= 4
        assert len(data["datasets"]) >= 10

    def test_get_dsr_mines_all_and_filtered(self):
        res = client.get("/api/real/dsr/mines")
        assert res.status_code == 200
        data = res.json()
        assert data["data_status"] == "source-derived"
        assert data["count"] >= 6
        assert len(data["mines"]) >= 6

        # Tehsil filter
        res_baihar = client.get("/api/real/dsr/mines?tehsil=Baihar")
        assert res_baihar.status_code == 200
        data_b = res_baihar.json()
        assert data_b["count"] >= 1
        assert any(m["mine_id"] == "MOIL_UKWA" for m in data_b["mines"])

    def test_get_dsr_mine_profile_success_and_404(self):
        res = client.get("/api/real/dsr/MOIL_BALAGHAT")
        assert res.status_code == 200
        data = res.json()
        assert data["mine_id"] == "MOIL_BALAGHAT"
        assert data["data_status"] == "source-derived"
        assert len(data["lease_areas"]) >= 1
        assert len(data["grade_reference"]) >= 1
        assert len(data["production_history"]) >= 1
        assert len(data["mine_plan_targets"]) >= 1
        assert len(data["constraints"]) >= 1

        # 404 test on invalid mine ID
        res_404 = client.get("/api/real/dsr/INVALID_MINE_999")
        assert res_404.status_code == 404
        assert "not found" in res_404.json()["detail"].lower()

    def test_get_dsr_mine_boundaries_success(self):
        res = client.get("/api/real/dsr/MOIL_BALAGHAT/boundaries")
        assert res.status_code == 200
        data = res.json()
        assert data["mine_id"] == "MOIL_BALAGHAT"
        assert data["data_status"] == "source-derived"
        assert data["polygon_geometry_status"] == "unavailable"
        assert data["point_geometry_status"] == "available"
        assert data["boundary_geojson"]["type"] == "FeatureCollection"
        assert len(data["boundary_pillars"]) >= 1

        res_ukwa = client.get("/api/real/dsr/MOIL_UKWA/boundaries")
        assert res_ukwa.status_code == 200
        assert data["polygon_geometry_status"] == "unavailable"
        assert len(res_ukwa.json()["boundary_pillars"]) >= 1

    def test_get_dsr_mine_geology(self):
        res = client.get("/api/real/dsr/MOIL_BALAGHAT/geology")
        assert res.status_code == 200
        data = res.json()
        assert data["formation_count"] == 7
        assert len(data["directly_associated_formations"]) >= 1
        assert data["directly_associated_formations"][0]["formation_name"] == "Mansar Formation"

    def test_get_dsr_mine_grade(self):
        res = client.get("/api/real/dsr/MOIL_BALAGHAT/grade")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] >= 3
        grades = data["grades"]
        assert any(g["grade_category"] == "High Grade Ferro-Manganese" for g in grades)

    def test_get_dsr_mine_exploration(self):
        res = client.get("/api/real/dsr/MOIL_BALAGHAT/exploration")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] >= 1
        exp = data["exploration_evidence"][0]
        assert exp["boreholes_drilled"] == 142
        assert exp["total_meterage_m"] == 28450.0

    def test_get_dsr_mine_production(self):
        res = client.get("/api/real/dsr/MOIL_BALAGHAT/production")
        assert res.status_code == 200
        data = res.json()
        assert len(data["reported_history"]) >= 5
        assert len(data["planned_targets"]) >= 3
        # Strict status separation check
        for r in data["reported_history"]:
            assert r["production_status"] == "reported_actual"
        for p in data["planned_targets"]:
            assert p["plan_status"] == "planned"

    def test_get_dsr_mine_constraints(self):
        res = client.get("/api/real/dsr/MOIL_BALAGHAT/constraints")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] >= 4
        categories = {c["constraint_category"] for c in data["constraints"]}
        assert "environmental" in categories
        assert "processing" in categories
        assert "safety_geotechnical" in categories

    def test_get_dsr_mine_context(self):
        res = client.get("/api/real/dsr/MOIL_BALAGHAT/context")
        assert res.status_code == 200
        data = res.json()
        assert data["mine_id"] == "MOIL_BALAGHAT"
        assert data["data_classification"] == "SOURCE-DERIVED / PARTIAL"
        assert data["geometry_status"] == "unavailable"
        assert len(data["lease_areas"]) >= 1
        assert len(data["directly_associated_formations"]) >= 1
        assert len(data["grade_distributions"]) >= 1
        assert "non_spatial" in data["spatial_status"]

        # 404 on invalid mine ID
        res_404 = client.get("/api/real/dsr/INVALID_MINE_999/context")
        assert res_404.status_code == 404

    def test_get_dsr_mine_evidence(self):
        res = client.get("/api/real/dsr/MOIL_BALAGHAT/evidence")
        assert res.status_code == 200
        data = res.json()
        assert data["mine_id"] == "MOIL_BALAGHAT"
        assert data["data_classification"] == "SOURCE-DERIVED"
        assert len(data["exploration_drilling_summary"]) >= 1
        assert "mineralization_evidence" in data
        assert "Not individual drillhole" in data["disclaimer"]

        # 404 on invalid mine ID
        res_404 = client.get("/api/real/dsr/INVALID_MINE_999/evidence")
        assert res_404.status_code == 404


class TestMineDashboardDsrIntegration:
    """Verifies that the consolidated mine dashboard exposes DSR source-derived availability."""

    def test_balaghat_dashboard_has_source_derived_dsr_data(self):
        summary = data_loader.get_mine_dashboard_summary("MOIL_BALAGHAT")
        assert summary["exists"] is True
        assert summary["point_type"] == "shaft_portal"
        assert summary["tehsil"] == "Balaghat"
        assert summary["lease_area_ha"] == 180.44

        categories = summary["data_availability_status"]
        assert "source_derived_data" in categories
        dsr_info = categories["source_derived_data"][0]
        assert dsr_info["category"] == "SOURCE-DERIVED"
        assert dsr_info["status"] == "AVAILABLE"
        assert "Balaghat DSR 2022" in dsr_info["source"]

    def test_non_balaghat_dashboard_dsr_unavailable(self):
        summary = data_loader.get_mine_dashboard_summary("MOIL_GUMGAON")
        assert summary["exists"] is True
        categories = summary["data_availability_status"]
        assert "source_derived_data" in categories
        dsr_info = categories["source_derived_data"][0]
        assert "UNAVAILABLE" in dsr_info["status"]


class TestDsrGovernanceRules:
    """
    Formal Verification of Governance Rules 6-10:
    Rule 6: Source-Scope Preservation
    Rule 7: No Implied Spatialization
    Rule 8: No Implied Temporalization
    Rule 9: Reserve / Resource Governance
    Rule 10: Constraint Governance
    """

    def test_rule_6_source_scope_preservation(self):
        """Rule 6: Every DSR record must retain its original scope without silent conversion."""
        # 1. Production reference maintains strict reporting levels
        prod_df = data_loader.load_dsr_production_reference()
        assert "reporting_level" in prod_df.columns
        assert "production_status" in prod_df.columns
        reporting_levels = set(prod_df["reporting_level"].unique())
        assert "mine_level" in reporting_levels or "district_aggregate" in reporting_levels or "company_level" in reporting_levels

        # Planned targets must have planned status
        targets_df = data_loader.load_dsr_mine_plan_targets()
        assert (targets_df["plan_status"] == "planned").all()
        assert not (targets_df["plan_status"] == "reported_actual").any()

        # Operational daily production remains isolated from annual reference
        daily_prod = data_loader.load_production_data()
        assert "actual_tonnes" in daily_prod.columns
        assert "date" in daily_prod.columns

    def test_rule_7_no_implied_spatialization(self):
        """Rule 7: Textual or aggregate DSR records must not be assigned to 30m grid or given fake coordinates."""
        # Check geology reference is non-spatial stratigraphy
        geo_df = data_loader.load_dsr_geology_reference()
        assert "latitude" not in geo_df.columns
        assert "longitude" not in geo_df.columns
        assert "polygon_geometry" not in geo_df.columns

        # Check API response explicitly tags spatial status as non-spatial
        res_context = client.get("/api/real/dsr/MOIL_BALAGHAT/context")
        assert res_context.status_code == 200
        data = res_context.json()
        assert "non_spatial" in data["spatial_status"]
        assert data["geometry_status"] == "unavailable"

        # Check aggregate exploration evidence has no individual fake collar coords
        exp_df = data_loader.load_dsr_exploration_evidence()
        assert "collar_latitude" not in exp_df.columns
        assert "collar_longitude" not in exp_df.columns

    def test_rule_8_no_implied_temporalization(self):
        """Rule 8: Annual/plan-period reference values must not be converted into daily/shift timestamps."""
        prod_df = data_loader.load_dsr_production_reference()
        # Verify financial_year format (e.g., "2021-22") without fake daily ISO timestamps
        for fy in prod_df["financial_year"]:
            assert "-" in str(fy) and len(str(fy)) in (7, 9)
            assert "T" not in str(fy)  # No fake ISO timestamps

        plan_df = data_loader.load_dsr_mine_plan_targets()
        for fy in plan_df["financial_year"]:
            assert "-" in str(fy)
            assert "T" not in str(fy)

    def test_rule_9_reserve_resource_governance(self):
        """Rule 9: UNFC resource classifications remain source-reported records, never ML predictions."""
        exp_df = data_loader.load_dsr_exploration_evidence()
        assert "unfc_reserves_111_mt" in exp_df.columns
        assert "unfc_remaining_resources_mt" in exp_df.columns
        assert "total_unfc_resources_mt" in exp_df.columns
        assert "source_name" in exp_df.columns
        assert (exp_df["data_status"] == "source-derived").all()

        # Check API evidence disclaimer
        res = client.get("/api/real/dsr/MOIL_BALAGHAT/evidence")
        assert res.status_code == 200
        data = res.json()
        assert data["data_classification"] == "SOURCE-DERIVED"
        assert "not individual" in data["disclaimer"].lower() or "documented" in data["disclaimer"].lower()

    def test_rule_10_constraint_governance(self):
        """Rule 10: Constraints require explicit numerical values, units, and scopes before being usable."""
        constraints_df = data_loader.load_dsr_constraints()
        assert "value" in constraints_df.columns
        assert "unit" in constraints_df.columns
        assert "constraint_status" in constraints_df.columns
        assert "source_name" in constraints_df.columns

        # Verify all numerical constraints have valid units and non-null values
        valid, errors = DataValidator.validate_dsr_constraints(constraints_df)
        assert valid, f"Constraint validation failed: {errors}"
        for _, row in constraints_df.iterrows():
            assert str(row["unit"]).strip() != ""
            assert pd.notnull(row["value"])
            assert pd.notnull(row["source_name"])


