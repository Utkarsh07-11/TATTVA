"""
Integration tests for FastAPI endpoints (SIH 2026 PS 26009).
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_root_and_health():
    res = client.get("/")
    assert res.status_code == 200

    h_res = client.get("/api/health")
    assert h_res.status_code == 200
    h_data = h_res.json()
    assert h_data["status"] in ("healthy", "degraded")


def test_mine_overview_and_metadata():
    res = client.get("/api/mine/overview?selected_block=BLOCK_A")
    assert res.status_code == 200
    data = res.json()
    assert "total_monthly_target" in data
    assert "aggregate_risk_level" in data
    assert len(data["blocks"]) == 3

    blocks_res = client.get("/api/mine/blocks")
    assert blocks_res.status_code == 200
    assert blocks_res.json()["type"] == "FeatureCollection"

    eq_res = client.get("/api/mine/equipment")
    assert eq_res.status_code == 200
    assert len(eq_res.json()["fleet"]) >= 5


def test_forecast_production():
    payload = {"mine_block_id": "BLOCK_A", "horizon_days": 30, "target_tonnes": 10000.0}
    res = client.post("/api/forecast/production", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["mine_block_id"] == "BLOCK_A"
    assert "forecast_tonnes" in data
    assert "interval_90" in data
    assert data["target_tonnes"] == 10000.0
    assert "risk_level" in data
    assert len(data["daily_points"]) == 30


def test_explain_shortfall():
    res = client.get("/api/explain/shortfall?mine_block_id=BLOCK_A&horizon_days=30")
    assert res.status_code == 200
    data = res.json()
    assert "contributors" in data
    assert len(data["contributors"]) > 0
    assert "narrative" in data
    assert "note" in data


def test_recommend_actions():
    res = client.get("/api/recommend/actions?mine_block_id=BLOCK_A&horizon_days=30")
    assert res.status_code == 200
    data = res.json()
    assert "options" in data
    assert len(data["options"]) >= 3
    assert data["options"][0]["rank"] == 1
    assert "expected_recovery_tonnes" in data["options"][0]


def test_simulate_scenario():
    payload = {
        "mine_block_id": "BLOCK_A",
        "horizon_days": 30,
        "equipment_availability_pct": 92.0,
        "blasting_delay_flag": 0,
        "rainfall_mm": 5.0
    }
    res = client.post("/api/simulate/scenario", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "simulated_tonnes" in data
    assert "expected_recovery_tonnes" in data


def test_prospectivity_map_and_resource():
    map_res = client.get("/api/prospectivity/map")
    assert map_res.status_code == 200
    map_data = map_res.json()
    assert map_data["type"] == "FeatureCollection"
    assert len(map_data["features"]) > 0

    dh_res = client.get("/api/prospectivity/drillholes")
    assert dh_res.status_code == 200
    assert len(dh_res.json()["features"]) > 0

    res_res = client.get("/api/prospectivity/resource-estimate?cutoff_grade_pct=20.0")
    assert res_res.status_code == 200
    assert "total_inferred_tonnes" in res_res.json()


def test_real_mines_endpoints():
    # 1. Get all 10 MOIL mines
    res = client.get("/api/real/mines")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 10
    assert data["data_status"] == "real"
    mines = data["mines"]
    assert len(mines) == 10

    required_fields = [
        "mine_id", "mine_name", "company", "state", "district",
        "mineral", "latitude", "longitude", "verification_status",
        "coordinate_precision", "source_title", "source_url", "data_status"
    ]
    for m in mines:
        for f in required_fields:
            assert f in m, f"Missing field {f} in mine {m.get('mine_id')}"
        assert m["data_status"] == "real"
        assert m["verification_status"] in ("verified_statutory_record", "verified_map_derived")
        assert 21.0 <= m["latitude"] <= 22.5
        assert 78.5 <= m["longitude"] <= 81.0

    # 2. Detail for Balaghat Mine
    bal_res = client.get("/api/real/mines/MOIL_BALAGHAT")
    assert bal_res.status_code == 200
    bal_data = bal_res.json()
    assert bal_data["mine_id"] == "MOIL_BALAGHAT"
    assert bal_data["layers"]["sentinel2_true_color"] is True
    assert bal_data["layers"]["ndvi"] is True
    assert bal_data["layers"]["elevation"] is True
    assert bal_data["layers"]["geology"] is False  # Digitization blocked

    # 3. Layer availability endpoint
    layers_res = client.get("/api/real/mines/MOIL_BALAGHAT/layers")
    assert layers_res.status_code == 200
    assert layers_res.json()["layers"]["ndvi"] is True

    # 4. Other mine layer check (e.g. Gumgaon)
    gum_res = client.get("/api/real/mines/MOIL_GUMGAON")
    assert gum_res.status_code == 200
    assert gum_res.json()["layers"]["ndvi"] is False  # Balaghat AOI only

    # 5. Non-existent mine -> 404
    err_res = client.get("/api/real/mines/INVALID_MINE_XYZ")
    assert err_res.status_code == 404


def test_real_production_endpoint():
    # 1. Full list
    res = client.get("/api/real/production")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 20
    assert data["data_status"] == "real"

    for r in data["records"]:
        assert r["production_tonnes"] > 0
        assert r["data_status"] == "reported"
        assert r["commodity"] == "Manganese Ore"

    # 2. Filter by period_type=annual
    ann_res = client.get("/api/real/production?period_type=annual")
    assert ann_res.status_code == 200
    ann_records = ann_res.json()["records"]
    assert len(ann_records) >= 15
    for r in ann_records:
        assert r["period_type"] == "annual"

    # 3. Filter by company=MOIL Limited
    moil_res = client.get("/api/real/production?company=MOIL+Limited")
    assert moil_res.status_code == 200
    for r in moil_res.json()["records"]:
        assert r["company"] == "MOIL Limited"


def test_real_rasters_summary_endpoint():
    res = client.get("/api/real/rasters/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 10
    rasters = data["rasters"]

    for r in rasters:
        assert "dataset_id" in r
        assert "dimensions" in r
        assert r["dimensions"]["height"] > 0
        assert r["dimensions"]["width"] > 0
        assert "crs" in r
        assert "resolution" in r
        assert "bounds" in r
        assert r["available"] is True

