"""
Unit tests for temporal and spatial feature engineering.
"""

import pytest
import pandas as pd
from src.data.loader import data_loader
from src.features.temporal import TemporalFeatureEngineer
from src.features.spatial import SpatialFeatureEngineer


def test_temporal_feature_engineering():
    df = data_loader.load_production_data()
    block_a = df[df["mine_block_id"] == "BLOCK_A"].copy()
    
    feat_df = TemporalFeatureEngineer.create_features(block_a)
    assert not feat_df.empty
    
    # Verify required lag & rolling features exist
    expected_cols = [
        "tonnes_lag_1", "tonnes_lag_7", "tonnes_lag_30",
        "avail_lag_1", "prod_roll_mean_7d", "prod_roll_std_7d",
        "avail_roll_mean_7d", "rain_roll_sum_7d", "day_of_week"
    ]
    for col in expected_cols:
        assert col in feat_df.columns, f"Missing feature column: {col}"
        
    # Check that lag 1 matches previous date's actual_tonnes
    sample_date = feat_df["date"].iloc[10]
    prev_date = sample_date - pd.Timedelta(days=1)
    expected_val = block_a[block_a["date"] == prev_date]["actual_tonnes"].values[0]
    assert feat_df["tonnes_lag_1"].iloc[10] == expected_val



def test_rolling_origin_cross_validation_splits():
    df = data_loader.load_production_data()
    block_a = df[df["mine_block_id"] == "BLOCK_A"].copy()
    feat_df = TemporalFeatureEngineer.create_features(block_a)
    
    splits = list(TemporalFeatureEngineer.rolling_origin_splits(feat_df, n_splits=4, test_window_days=30))
    assert len(splits) == 4
    
    for train_df, test_df in splits:
        # Check temporal order: maximum train date strictly precedes minimum test date
        assert train_df["date"].max() < test_df["date"].min()
        assert len(test_df) == 30


def test_spatial_block_clustering():
    dh_df = data_loader.load_drillhole_assay()
    sat_df = data_loader.load_satellite_grid()
    
    fused_df = SpatialFeatureEngineer.sample_satellite_at_drillholes(dh_df, sat_df)
    assert "iron_oxide_index" in fused_df.columns
    assert "slope_deg" in fused_df.columns
    
    splits = list(SpatialFeatureEngineer.spatial_block_splits(fused_df, n_blocks=4))
    assert len(splits) == 4
    
    for tr, val in splits:
        assert not tr.empty
        assert not val.empty
        # Verify disjoint spatial blocks
        tr_blocks = set(tr["spatial_block"].unique())
        val_blocks = set(val["spatial_block"].unique())
        assert len(tr_blocks.intersection(val_blocks)) == 0
