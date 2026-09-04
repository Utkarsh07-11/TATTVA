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
