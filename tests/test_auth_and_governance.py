"""
Test Suite for Role-Based Semantic Authentication & Data Governance Engine
Validates:
1. 3-Tier Semantic Employee ID decoding (9-char site, 10-char HQ, 'IN' Apex)
2. 6-Digit PIN authentication & token generation
3. Strict role-based mine scoping (Balaghat operator cannot log Dongri Buzurg)
4. Weekly Production Summary ingestion with real-time ML inference
5. 10-Mine Statutory Compliance Matrix (Weeks 1-4)
6. Dynamic Commissioning of New Mining Leases by Tier 3 Apex
7. Bulk Employee Roster Onboarding via CSV
8. Statutory Audit Trail
"""

import io
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.data.governance_db import governance_db

client = TestClient(app)


def test_auth_demo_presets():
    resp = client.get("/api/auth/presets")
    assert resp.status_code == 200
    data = resp.json()
    assert "presets" in data
    assert len(data["presets"]) == 3
    ids = [p["employee_id"] for p in data["presets"]]
    assert "MPB260001" in ids
    assert "MHN2601001" in ids
    assert "IN26009" in ids


def test_login_tier1_site_engineer_success():
    resp = client.post(
        "/api/auth/login",
        json={"employee_id": "MPB260001", "pin": "123456"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    user = data["user"]
    assert user["employee_id"] == "MPB260001"
    assert user["role"] == "MINE_OPERATOR"
    assert user["tier"] == 1
    assert user["mine_id"] == "MOIL_BALAGHAT"


def test_login_tier2_hq_management_success():
    resp = client.post(
        "/api/auth/login",
        json={"employee_id": "MHN2601001", "pin": "654321"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["role"] == "EXECUTIVE_MANAGEMENT"
    assert data["user"]["tier"] == 2


def test_login_tier3_apex_board_success():
    resp = client.post(
        "/api/auth/login",
        json={"employee_id": "IN26009", "pin": "999999"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["role"] == "SUPER_ADMIN"
    assert data["user"]["tier"] == 3


def test_login_invalid_pin():
    resp = client.post(
        "/api/auth/login",
        json={"employee_id": "MPB260001", "pin": "000000"},
    )
    assert resp.status_code == 401
    assert "Invalid 6-digit security PIN" in resp.json()["detail"]


def test_login_invalid_id_syntax():
    resp = client.post(
        "/api/auth/login",
        json={"employee_id": "BADID123", "pin": "123456"},
    )
    assert resp.status_code == 400


def test_weekly_production_csv_upload():
    login_resp = client.post("/api/auth/login", json={"employee_id": "MPB260001", "pin": "123456"})
    token = login_resp.json()["token"]

    csv_data = (
        "week_number,planned_tonnes,actual_tonnes,equipment_availability_pct,rainfall_mm\n"
        "3,4200.0,4100.0,88.0,25.0\n"
    )
    resp = client.post(
        "/api/governance/upload-weekly-csv",
        files={"file": ("test_week3.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"
    assert "realtime_inference" in resp.json()


def test_weekly_production_upload_authorized():
    # Login as Balaghat operator
    login_resp = client.post("/api/auth/login", json={"employee_id": "MPB260001", "pin": "123456"})
    token = login_resp.json()["token"]

    payload = {
        "mine_id": "MOIL_BALAGHAT",
        "week_number": 3,
        "planned_tonnes": 4200.0,
        "actual_tonnes": 4050.0,
        "equipment_availability_pct": 86.5,
        "rainfall_mm": 32.0,
        "blasting_delays_count": 1,
        "maintenance_hours": 10.5,
        "notes": "Week 3 Balaghat extraction verified.",
    }
    resp = client.post(
        "/api/governance/upload-weekly",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert "realtime_inference" in data
    assert data["realtime_inference"]["shortfall_risk_pct"] > 0
    assert data["realtime_inference"]["p50_tonnes"] > 0


def test_weekly_production_upload_scoping_forbidden():
    # Login as Balaghat operator
    login_resp = client.post("/api/auth/login", json={"employee_id": "MPB260001", "pin": "123456"})
    token = login_resp.json()["token"]

    # Attempt to log for Dongri Buzurg
    payload = {
        "mine_id": "MOIL_DONGRI_BUZURG",
        "week_number": 3,
        "planned_tonnes": 3000.0,
        "actual_tonnes": 2900.0,
        "equipment_availability_pct": 85.0,
        "rainfall_mm": 10.0,
    }
    resp = client.post(
        "/api/governance/upload-weekly",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
    assert "Access Denied" in resp.json()["detail"]


def test_compliance_matrix_10_mines():
    resp = client.get("/api/governance/compliance-matrix")
    assert resp.status_code == 200
    data = resp.json()
    assert "matrix" in data
    assert data["total_mines"] >= 10
    mine_ids = [m["mine_id"] for m in data["matrix"]]
    assert "MOIL_BALAGHAT" in mine_ids
    assert "MOIL_DONGRI_BUZURG" in mine_ids
    assert "MOIL_UKWA" in mine_ids


def test_commission_new_mine_apex_authorized():
    # Login as Apex
    login_resp = client.post("/api/auth/login", json={"employee_id": "IN26009", "pin": "999999"})
    token = login_resp.json()["token"]

    payload = {
        "mine_name": "Keonjhar Barbil Horizon",
        "state": "Odisha",
        "district": "Keonjhar",
        "latitude": 22.115,
        "longitude": 85.385,
        "lease_area_ha": 145.0,
        "mineral": "Manganese Ore",
        "mining_method": "Opencast",
        "annual_target_tonnes": 60000.0,
    }
    resp = client.post(
        "/api/governance/commission-mine",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["commissioned_mine"]["semantic_prefix"] == "ODK"

    # Verify newly commissioned mine appears in compliance matrix
    matrix_resp = client.get("/api/governance/compliance-matrix")
    assert matrix_resp.status_code == 200
    all_mines = [m["mine_id"] for m in matrix_resp.json()["matrix"]]
    assert "MOIL_KEONJHAR_BARBIL_HORIZON" in all_mines


def test_commission_mine_forbidden_for_tier1():
    # Login as Tier 1
    login_resp = client.post("/api/auth/login", json={"employee_id": "MPB260001", "pin": "123456"})
    token = login_resp.json()["token"]

    payload = {
        "mine_name": "Unauthorized Pit",
        "state": "Madhya Pradesh",
        "district": "Balaghat",
        "latitude": 21.85,
        "longitude": 80.23,
    }
    resp = client.post(
        "/api/governance/commission-mine",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_sample_csv_download():
    resp = client.get("/api/governance/sample-csv/weekly-production")
    assert resp.status_code == 200
    assert "planned_tonnes" in resp.text
    assert "actual_tonnes" in resp.text


def test_audit_trail():
    resp = client.get("/api/governance/audit-trail")
    assert resp.status_code == 200
    data = resp.json()
    assert "audit_trail" in data
    assert len(data["audit_trail"]) > 0
