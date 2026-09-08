"""
Test suite for Phase 10 Real Prospectivity API endpoints.
Tests metadata retrieval, GeoJSON polygon generation (27,720 cells),
authoritative evidence points, multi-mine gating, and scientific disclaimers.
"""

from fastapi.testclient import TestClient
import numpy as np
import pytest

from src.api.main import app
from src.data.loader import data_loader

client = TestClient(app)


def test_real_prospectivity_metadata_balaghat():
    """Test /api/real/prospectivity/MOIL_BALAGHAT returns complete metadata."""
    response = client.get("/api/real/prospectivity/MOIL_BALAGHAT")
    assert response.status_code == 200
    data = response.json()

    assert data["mine_id"] == "MOIL_BALAGHAT"
    assert data["is_available"] is True
    assert data["data_status"] == "derived_from_real_data"
    assert data["total_cells"] == 27720
    assert data["valid_cells"] == 27487
    assert data["partial_cells"] == 233
    assert data["grid_resolution_m"] == 30.0
    assert data["crs"] == "EPSG:32644"

    # Verify features and limitations
    assert len(data["features_used"]) == 16
    assert len(data["critical_scientific_limitations"]) == 7
    assert len(data["available_layers"]) == 4

    # Check layer names contain no "probability"
    for layer in data["available_layers"]:
        assert "probability" not in layer["name"].lower()
        assert "ore" not in layer["name"].lower()


def test_real_prospectivity_geojson_balaghat():
    """Test /api/real/prospectivity/MOIL_BALAGHAT/geojson returns 27,720 cells."""
    response = client.get("/api/real/prospectivity/MOIL_BALAGHAT/geojson")
    assert response.status_code == 200
    geojson = response.json()

    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 27720

    first_feat = geojson["features"][0]
    assert first_feat["geometry"]["type"] == "Polygon"
    assert len(first_feat["geometry"]["coordinates"][0]) == 5

    p = first_feat["properties"]
    assert "cell_id" in p
    assert "exploration_priority_score" in p
    assert "anomaly_score" in p
    assert "robust_distance_score" in p
    assert "positive_anchor_similarity" in p
    assert "feature_quality" in p
    assert p["feature_quality"] in ["valid", "partial"]

    # Verify scores are finite and in [0, 1]
    for key in ["exploration_priority_score", "anomaly_score", "robust_distance_score", "positive_anchor_similarity"]:
        val = p[key]
        assert isinstance(val, (int, float))
        assert 0.0 <= val <= 1.0


def test_real_mineralization_evidence_balaghat():
    """Test /api/real/prospectivity/MOIL_BALAGHAT/evidence returns verified anchors."""
    response = client.get("/api/real/prospectivity/MOIL_BALAGHAT/evidence")
    assert response.status_code == 200
    evidence = response.json()

    assert evidence["type"] == "FeatureCollection"
    assert len(evidence["features"]) >= 1

    # Verify Bharweli shaft portal is present and tagged as primary similarity anchor
    shaft_anchor = next(
        (f for f in evidence["features"] if f["properties"]["evidence_id"] == "EVID_MOIL_BALAGHAT_BHARWELI_01"),
        None
    )
    assert shaft_anchor is not None
    assert shaft_anchor["properties"]["in_aoi"] is True
    assert "similarity anchor" in shaft_anchor["properties"]["role_in_experiment"].lower()


def test_real_prospectivity_multi_mine_isolation():
    """Verify non-Balaghat mines return unavailable status and no Balaghat data."""
    other_mines = ["MOIL_TIRODI", "MOIL_UKWA", "MOIL_MANSAR", "MOIL_DONGRI_BUZURG"]

    for mine_id in other_mines:
        meta_res = client.get(f"/api/real/prospectivity/{mine_id}")
        assert meta_res.status_code == 200
        meta_data = meta_res.json()
        assert meta_data["is_available"] is False
        assert meta_data["data_status"] == "unavailable"

        geo_res = client.get(f"/api/real/prospectivity/{mine_id}/geojson")
        assert geo_res.status_code == 200
        geo_data = geo_res.json()
        assert len(geo_data["features"]) == 0
