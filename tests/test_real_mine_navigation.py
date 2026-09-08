"""
Tests for Phase 11: 10-Mine Navigation + Real Mine Intelligence Experience
Verifies MOIL statutory 10-mine registry source of truth, 5-category Data Availability Status,
consolidated mine dashboard endpoint, multi-mine isolation, and company-level production scope.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

EXPECTED_10_MINE_IDS = {
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
}


def test_real_mines_registry_10_mines_integrity():
    """Verify registry dynamically returns exactly 10 audited MOIL statutory mines."""
    response = client.get("/api/real/mines")
    assert response.status_code == 200
    data = response.json()

    assert data["count"] == 10
    assert len(data["mines"]) == 10

    returned_ids = {m["mine_id"] for m in data["mines"]}
    assert returned_ids == EXPECTED_10_MINE_IDS

    # Verify states and coordinate presence
    states = {m["state"] for m in data["mines"]}
    assert "Madhya Pradesh" in states
    assert "Maharashtra" in states

    for mine in data["mines"]:
        assert isinstance(mine["latitude"], float)
        assert isinstance(mine["longitude"], float)
        assert mine["company"] == "MOIL Limited"
        assert mine["verification_status"] in ("verified_statutory_record", "verified_map_derived")
        assert "coordinate_precision" in mine
        assert "source_title" in mine


def test_mine_dashboard_balaghat_availability_status():
    """Verify Balaghat mine dashboard reports real exploration, satellite, and 5-category availability."""
    response = client.get("/api/real/mine-dashboard/MOIL_BALAGHAT")
    assert response.status_code == 200
    data = response.json()

    assert data["exists"] is True
    assert data["mine_id"] == "MOIL_BALAGHAT"
    assert data["mine_name"] == "Balaghat"
    assert data["exploration_available"] is True

    # Check 5 categories in Data Availability Status
    avail = data["data_availability_status"]
    assert "real_data" in avail
    assert "reported_data" in avail
    assert "experimental" in avail
    assert "simulation" in avail
    assert "unavailable" in avail

    # Real data should be available for Balaghat
    satellite_item = next(item for item in avail["real_data"] if "Satellite" in item["name"])
    assert satellite_item["status"] == "AVAILABLE"
    assert satellite_item["category"] == "REAL DATA"

    # Exploration priority experimental layer available for Balaghat
    exp_item = avail["experimental"][0]
    assert exp_item["status"] == "AVAILABLE"
    assert exp_item["cells"] == 27720
    assert "Relative ranking heuristic, not probability" in exp_item["disclaimer"]

    # Reported production scope note
    rep_item = avail["reported_data"][0]
    assert rep_item["category"] == "REPORTED DATA"
    assert "Company-level aggregate" in rep_item["scope_note"]

    # Simulation item
    sim_item = avail["simulation"][0]
    assert sim_item["category"] == "SIMULATION"
    assert sim_item["name"] == "TATTVA Operational Simulation"


def test_mine_dashboard_non_balaghat_isolation():
    """Verify non-Balaghat mines cleanly report exploration and raster layers as unavailable."""
    non_balaghat_mines = ["MOIL_TIRODI", "MOIL_UKWA", "MOIL_CHIKLA", "MOIL_DONGRI_BUZURG", "MOIL_GUMGAON"]

    for mine_id in non_balaghat_mines:
        response = client.get(f"/api/real/mine-dashboard/{mine_id}")
        assert response.status_code == 200
        data = response.json()

        assert data["exists"] is True
        assert data["mine_id"] == mine_id
        assert data["exploration_available"] is False

        avail = data["data_availability_status"]

        # Satellite & DEM should be unavailable
        for real_item in avail["real_data"]:
            assert real_item["status"] == "UNAVAILABLE"

        # Experimental exploration should be unavailable
        for exp_item in avail["experimental"]:
            assert exp_item["status"] == "UNAVAILABLE"
            assert exp_item["cells"] == 0

        # Company-level reported production remains available aggregate
        assert avail["reported_data"][0]["status"] == "AVAILABLE_AGGREGATE"


def test_mine_dashboard_invalid_mine_404():
    """Verify invalid mine ID returns 404 without crashing."""
    response = client.get("/api/real/mine-dashboard/INVALID_MINE_ID")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_prospectivity_geojson_isolation_no_leakage():
    """Verify non-Balaghat mines return empty GeoJSON without leaking Balaghat cells."""
    for mine_id in ["MOIL_TIRODI", "MOIL_UKWA", "MOIL_CHIKLA"]:
        response = client.get(f"/api/real/prospectivity/{mine_id}/geojson")
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["is_available"] is False
        assert len(data["features"]) == 0


def test_production_scope_integrity():
    """Verify reported production maintains company-level aggregate status and does not attribute to specific mines."""
    response = client.get("/api/real/production?company=MOIL%20Limited&period_type=annual")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0

    for rec in data["records"]:
        assert rec["company"] == "MOIL Limited"
        assert rec["commodity"] == "Manganese Ore"
        assert rec["mine"] == "ALL_MINES_AGGREGATE"  # Crucial: Not attributed to individual mine
        assert rec["production_tonnes"] > 0
