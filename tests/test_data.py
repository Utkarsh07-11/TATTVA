"""
Unit tests for data generation, schema validation, and loading.
"""

import pytest
import pandas as pd
from src.data.loader import data_loader
from src.data.validator import DataValidator


def test_production_data_loading_and_validation():
    df = data_loader.load_production_data()
    assert not df.empty
    assert len(df) >= 1000
    
    valid, errors = DataValidator.validate_production(df)
    assert valid, f"Production data validation failed: {errors}"
    assert "mine_block_id" in df.columns
    assert set(df["mine_block_id"].unique()) == {"BLOCK_A", "BLOCK_B", "BLOCK_C"}
    assert df["actual_tonnes"].min() >= 0.0


def test_drillhole_data_loading_and_validation():
    df = data_loader.load_drillhole_assay()
    assert not df.empty
    assert len(df) >= 100
    
    valid, errors = DataValidator.validate_drillholes(df)
    assert valid, f"Drillhole data validation failed: {errors}"
    assert df["mn_grade_pct"].min() >= 0.0
    assert df["mn_grade_pct"].max() <= 100.0
    assert df["hole_id"].nunique() == len(df)


def test_satellite_grid_loading_and_validation():
    df = data_loader.load_satellite_grid()
    assert not df.empty
    
    valid, errors = DataValidator.validate_satellite_grid(df)
    assert valid, f"Satellite grid validation failed: {errors}"
    assert "iron_oxide_index" in df.columns
    assert "clay_index" in df.columns
    assert df["ndvi"].between(-1.0, 1.0).all()


def test_mine_blocks_geojson_structure():
    geojson = data_loader.load_mine_blocks_geojson()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) >= 3
    for f in geojson["features"]:
        assert f["geometry"]["type"] == "Polygon"
        assert "block_id" in f["properties"]
