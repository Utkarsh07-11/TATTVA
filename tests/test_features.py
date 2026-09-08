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


def test_raster_extractor_point_sampling_and_crs_transform():
    from config.settings import settings
    from src.features.raster_extractor import RasterExtractor

    ndvi_path = settings.DERIVED_DATA_DIR / "sentinel2" / "balaghat" / "ndvi.tif"
    assert ndvi_path.exists(), "NDVI raster must exist"

    extractor = RasterExtractor(ndvi_path, feature_name="NDVI")
    meta = extractor.get_metadata()
    assert meta["feature_name"] == "NDVI"
    assert "EPSG:32644" in meta["crs"]
    assert meta["nodata"] == -9999.0

    # 1. Sample in native UTM 44N
    val, is_valid = extractor.sample_point(420236.56, 2416025.70, input_crs="EPSG:32644")
    assert is_valid is True
    assert val is not None
    assert -1.0 <= val <= 1.0

    # 2. Sample in WGS84 Geographic coords (MOIL Balaghat Anchor: 80.2281E, 21.8464N)
    val_wgs84, is_valid_wgs84 = extractor.sample_point(80.2281, 21.8464, input_crs="EPSG:4326")
    assert is_valid_wgs84 is True
    assert val_wgs84 is not None
    assert abs(val - val_wgs84) < 1e-3, "UTM and transformed WGS84 sample should match"


def test_raster_extractor_out_of_bounds_and_nodata():
    from config.settings import settings
    from src.features.raster_extractor import RasterExtractor

    elev_path = settings.DERIVED_DATA_DIR / "dem" / "balaghat" / "elevation.tif"
    assert elev_path.exists(), "Elevation raster must exist"

    extractor = RasterExtractor(elev_path, feature_name="elevation")

    # Point far outside Balaghat AOI (e.g. Mumbai 72.8E, 19.0N)
    val_out, is_valid_out = extractor.sample_point(72.8777, 19.0760, input_crs="EPSG:4326")
    assert is_valid_out is False
    assert pd.isna(val_out) or val_out is None


def test_multi_raster_extractor_grid_generation_and_batch():
    from config.settings import settings
    from src.features.raster_extractor import MultiRasterExtractor

    extractor = MultiRasterExtractor()
    s2_dir = settings.DERIVED_DATA_DIR / "sentinel2" / "balaghat"
    dem_dir = settings.DERIVED_DATA_DIR / "dem" / "balaghat"

    extractor.register_raster("NDVI", s2_dir / "ndvi.tif")
    extractor.register_raster("elevation", dem_dir / "elevation.tif")

    catalog = extractor.get_catalog()
    assert "NDVI" in catalog
    assert "elevation" in catalog

    # Sample batch points
    test_points = [
        (420236.56, 2416025.70),  # Inside Balaghat
        (421000.00, 2417000.00),  # Inside Balaghat
        (100000.00, 1000000.00),  # Outside bounds
    ]

    extracted_df = extractor.extract_features(test_points, input_crs="EPSG:32644", include_quality=True)
    assert len(extracted_df) == 3
    assert "NDVI" in extracted_df.columns
    assert "elevation" in extracted_df.columns
    assert "valid_feature_fraction" in extracted_df.columns
    assert "feature_quality" in extracted_df.columns

    # First two points are valid inside bounds
    assert extracted_df["feature_quality"].iloc[0] == "valid"
    assert extracted_df["feature_quality"].iloc[1] == "valid"
    assert extracted_df["feature_quality"].iloc[2] == "invalid"
    assert extracted_df["valid_feature_fraction"].iloc[2] == 0.0

    # Grid generator test
    bounds = (417722.89, 2413543.90, 418022.89, 2413843.90)  # 300m x 300m test box
    grid = MultiRasterExtractor.generate_regular_grid(bounds, spacing_m=30.0, crs="EPSG:32644")
    assert len(grid) == 100  # 10 x 10 cells
    assert list(grid.columns) == ["cell_id", "x", "y", "longitude", "latitude"]
