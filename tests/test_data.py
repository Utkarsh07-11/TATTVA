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


def test_real_moil_mines_registry():
    from config.settings import settings
    import json

    mines_file = settings.REAL_DATA_DIR / "moil" / "mines.csv"
    manifest_file = settings.REAL_DATA_DIR / "moil" / "source_manifest.json"
    audit_file = settings.REAL_DATA_DIR / "moil" / "coordinate_audit.md"

    assert mines_file.exists(), f"Mines registry not found at {mines_file}"
    assert manifest_file.exists(), f"Source manifest not found at {manifest_file}"
    assert audit_file.exists(), f"Audit file not found at {audit_file}"

    df = pd.read_csv(mines_file)
    expected_cols = [
        "mine_id", "mine_name", "company", "state",
        "district", "mineral", "data_source", "verification_status",
        "latitude", "longitude", "coordinate_interpretation",
        "coordinate_precision", "source_title", "source_url",
        "page_section", "evidence_notes"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing expected column {col}"

    assert len(df) == 10, f"Expected 10 core MOIL mines, found {len(df)}"

    expected_mines = {
        "Balaghat", "Ukwa", "Tirodi", "Sitapatore",
        "Chikla", "Dongri Buzurg", "Beldongri",
        "Kandri", "Munsar", "Gumgaon"
    }
    assert set(df["mine_name"]) == expected_mines

    # Audit verification status checks
    valid_statuses = {"verified_statutory_record", "verified_map_derived", "needs_source_verification"}
    assert df["verification_status"].isin(valid_statuses).all()

    # Verified coordinates must have proper provenance and non-empty URLs
    verified_rows = df[df["verification_status"].isin({"verified_statutory_record", "verified_map_derived"})]
    assert len(verified_rows) == 10

    # Coordinates must fall within Central India Manganese Belt bounding box
    assert verified_rows["latitude"].between(21.0, 22.5).all(), "Latitudes out of valid belt range"
    assert verified_rows["longitude"].between(78.5, 81.0).all(), "Longitudes out of valid belt range"

    # Every verified location must have title, URL, section, and evidence notes
    assert verified_rows["source_title"].notna().all()
    assert (verified_rows["source_title"].str.len() > 5).all()
    assert verified_rows["source_url"].str.startswith("http").all()
    assert verified_rows["evidence_notes"].notna().all()
    assert (verified_rows["evidence_notes"].str.len() > 10).all()

    with open(manifest_file, "r") as f:
        manifest = json.load(f)
    assert manifest["dataset_name"]
    assert manifest["operating_company"]
    assert len(manifest["provenance_by_mine"]) == 10


def test_real_moil_mine_locations_geojson():
    from config.settings import settings
    import json

    geojson_file = settings.REAL_DATA_DIR / "moil" / "mine_locations.geojson"
    mines_file = settings.REAL_DATA_DIR / "moil" / "mines.csv"
    assert geojson_file.exists(), f"GeoJSON not found at {geojson_file}"

    with open(geojson_file, "r") as f:
        data = json.load(f)

    df = pd.read_csv(mines_file)

    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == len(df)

    required_props = [
        "mine_id", "mine_name", "company", "state",
        "district", "mineral", "verification_status",
        "coordinate_interpretation", "coordinate_precision",
        "source_title", "source_url", "page_section", "evidence_notes"
    ]

    for f in data["features"]:
        assert f["type"] == "Feature"
        assert f["geometry"]["type"] == "Point"
        lon, lat = f["geometry"]["coordinates"]
        assert 78.5 <= lon <= 81.0, f"Longitude {lon} out of range"
        assert 21.0 <= lat <= 22.5, f"Latitude {lat} out of range"

        props = f["properties"]
        for prop in required_props:
            assert prop in props, f"Missing property {prop} in {props.get('mine_id')}"

        # Ensure GeoJSON coordinates match CSV exactly
        csv_row = df[df["mine_id"] == props["mine_id"]].iloc[0]
        assert round(lon, 4) == round(csv_row["longitude"], 4)
        assert round(lat, 4) == round(csv_row["latitude"], 4)


def test_sentinel2_balaghat_aoi_and_features():
    from config.settings import settings
    import json
    import rasterio
    import numpy as np

    s2_real_dir = settings.REAL_DATA_DIR / "sentinel2" / "balaghat"
    s2_derived_dir = settings.DERIVED_DATA_DIR / "sentinel2" / "balaghat"

    aoi_file = s2_real_dir / "aoi.geojson"
    metadata_file = s2_real_dir / "metadata.json"
    summary_file = s2_derived_dir / "feature_summary.json"

    assert aoi_file.exists(), f"AOI file not found at {aoi_file}"
    assert metadata_file.exists(), f"Metadata file not found at {metadata_file}"
    assert summary_file.exists(), f"Feature summary not found at {summary_file}"

    # 1. AOI validation & anchor containment
    with open(aoi_file, "r") as f:
        aoi = json.load(f)
    assert aoi["type"] == "FeatureCollection"
    feat = aoi["features"][0]
    assert feat["geometry"]["type"] == "Polygon"
    coords = feat["geometry"]["coordinates"][0]
    min_x = min(pt[0] for pt in coords)
    max_x = max(pt[0] for pt in coords)
    min_y = min(pt[1] for pt in coords)
    max_y = max(pt[1] for pt in coords)
    anchor_lon, anchor_lat = 80.2281, 21.8464
    assert (min_x <= anchor_lon <= max_x) and (min_y <= anchor_lat <= max_y), "Anchor coordinate outside AOI"

    # 2. Metadata provenance & source URLs validation
    with open(metadata_file, "r") as f:
        meta = json.load(f)
    required_meta_keys = [
        "source", "provider", "product_id", "satellite",
        "acquisition_date", "processing_level", "cloud_cover_pct",
        "aoi", "bands", "crs", "resolution_m", "download_date",
        "processing_steps"
    ]
    for key in required_meta_keys:
        assert key in meta, f"Missing metadata key {key}"
    assert meta["processing_level"] == "Level-2A (Bottom-of-Atmosphere Surface Reflectance)"
    assert meta["cloud_cover_pct"] < 1.0  # Low cloud scene
    assert meta["credentials_required"] is False
    assert len(meta["bands"]) == 7
    for band_info in meta["bands"]:
        assert band_info["source_url"].startswith("http"), f"Missing source URL for {band_info['band']}"

    # 3. Raw band files and native resolution validation
    raw_dir = s2_real_dir / "raw"
    expected_10m_bands = ["B02.tif", "B03.tif", "B04.tif", "B08.tif", "TCI.tif"]
    for b in expected_10m_bands:
        raw_file = raw_dir / b
        assert raw_file.exists(), f"Raw band {b} not found at {raw_file}"
        with rasterio.open(raw_file) as src:
            assert src.shape == (496, 503), f"10m band {b} shape mismatch"
            assert src.res == (10.0, 10.0), f"10m band {b} res mismatch"

    expected_20m_bands = ["B11.tif", "B12.tif"]
    for b in expected_20m_bands:
        raw_file = raw_dir / b
        assert raw_file.exists(), f"Raw band {b} not found at {raw_file}"
        with rasterio.open(raw_file) as src:
            assert src.shape == (248, 251), f"20m band {b} shape mismatch"
            assert src.res == (20.0, 20.0), f"20m band {b} res mismatch"

    # 4. Derived analytical GeoTIFFs validation
    expected_derived = ["ndvi.tif", "ndwi.tif", "red_nir_ratio.tif", "swir_nir_ratio.tif"]
    ref_transform = None
    ref_shape = None

    for fname in expected_derived:
        rast_path = s2_derived_dir / fname
        assert rast_path.exists(), f"Derived raster {fname} not found"
        with rasterio.open(rast_path) as src:
            assert src.crs.to_epsg() == 32644, f"Invalid CRS {src.crs}"
            assert src.count == 1
            data = src.read(1)
            valid_mask = data != -9999.0
            assert valid_mask.sum() > 200000, "Too few valid pixels"

            # Check no NaN, +Inf, -Inf
            assert not np.isnan(data).any(), f"NaN found in {fname}"
            assert not np.isinf(data).any(), f"Inf found in {fname}"

            if ref_shape is None:
                ref_shape = src.shape
                ref_transform = src.transform
            else:
                assert src.shape == ref_shape, f"Shape mismatch in {fname}"
                assert src.transform == ref_transform, f"Spatial alignment mismatch in {fname}"

            if fname == "ndvi.tif":
                assert data[valid_mask].min() >= -1.0
                assert data[valid_mask].max() <= 1.0
            elif fname == "ndwi.tif":
                assert data[valid_mask].min() >= -1.0
                assert data[valid_mask].max() <= 1.0

    # 5. Visual products validation
    for img_name in ["true_color.png", "ndvi.png"]:
        img_path = s2_derived_dir / img_name
        assert img_path.exists(), f"Visual product {img_name} not found"
        assert img_path.stat().st_size > 10000, f"Visual product {img_name} is too small"


def test_dem_balaghat_aoi_and_features():
    from config.settings import settings
    import json
    import rasterio
    import numpy as np

    dem_real_dir = settings.REAL_DATA_DIR / "dem" / "balaghat"
    dem_derived_dir = settings.DERIVED_DATA_DIR / "dem" / "balaghat"

    aoi_file = dem_real_dir / "aoi.geojson"
    metadata_file = dem_real_dir / "metadata.json"
    summary_file = dem_derived_dir / "feature_summary.json"

    assert aoi_file.exists(), f"AOI file not found at {aoi_file}"
    assert metadata_file.exists(), f"Metadata file not found at {metadata_file}"
    assert summary_file.exists(), f"Feature summary not found at {summary_file}"

    # 1. AOI validation & anchor containment
    with open(aoi_file, "r") as f:
        aoi = json.load(f)
    assert aoi["type"] == "FeatureCollection"
    coords = aoi["features"][0]["geometry"]["coordinates"][0]
    min_x = min(pt[0] for pt in coords)
    max_x = max(pt[0] for pt in coords)
    min_y = min(pt[1] for pt in coords)
    max_y = max(pt[1] for pt in coords)
    anchor_lon, anchor_lat = 80.2281, 21.8464
    assert (min_x <= anchor_lon <= max_x) and (min_y <= anchor_lat <= max_y), "Anchor coordinate outside AOI"

    # 2. Metadata validation
    with open(metadata_file, "r") as f:
        meta = json.load(f)
    required_meta_keys = [
        "provider", "dataset_name", "tile_name", "source_url",
        "download_url", "access_method", "credentials_required",
        "native_crs", "native_resolution", "processing_crs",
        "processing_resolution_m", "vertical_units", "vertical_datum",
        "horizontal_units", "nodata_value", "aoi"
    ]
    for k in required_meta_keys:
        assert k in meta, f"Missing metadata key {k}"
    assert meta["credentials_required"] is False
    assert "Copernicus" in meta["dataset_name"]

    # 3. Raw DEM validation
    raw_dem_file = dem_real_dir / "raw" / "copernicus_dem_30m_balaghat.tif"
    assert raw_dem_file.exists(), f"Raw DEM file not found at {raw_dem_file}"
    with rasterio.open(raw_dem_file) as src:
        assert src.shape == (162, 174)
        assert src.crs.to_epsg() == 4326

    # 4. Derived terrain rasters validation
    expected_derived = ["elevation.tif", "slope.tif", "aspect.tif", "hillshade.tif"]
    ref_shape = None
    ref_transform = None

    for fname in expected_derived:
        rast_path = dem_derived_dir / fname
        assert rast_path.exists(), f"Derived DEM raster {fname} not found"
        with rasterio.open(rast_path) as src:
            assert src.crs.to_epsg() == 32644, f"Invalid CRS in {fname}"
            assert src.res == (30.0, 30.0), f"Invalid resolution in {fname}"
            assert src.nodata == -9999.0, f"Invalid nodata in {fname}"
            data = src.read(1)

            # Check no NaN / Inf
            assert not np.isnan(data).any(), f"NaN found in {fname}"
            assert not np.isinf(data).any(), f"Inf found in {fname}"

            valid_mask = data != -9999.0
            assert valid_mask.sum() > 25000, f"Too few valid pixels in {fname}"

            if ref_shape is None:
                ref_shape = src.shape
                ref_transform = src.transform
            else:
                assert src.shape == ref_shape, f"Shape mismatch in {fname}"
                assert src.transform == ref_transform, f"Spatial alignment mismatch in {fname}"

            valid_data = data[valid_mask]
            if fname == "elevation.tif":
                assert 200.0 <= valid_data.min() <= 400.0
                assert 450.0 <= valid_data.max() <= 700.0
            elif fname == "slope.tif":
                assert valid_data.min() >= 0.0
                assert valid_data.max() <= 90.0
            elif fname == "aspect.tif":
                assert valid_data.min() >= -1.0
                assert valid_data.max() <= 360.0
            elif fname == "hillshade.tif":
                assert valid_data.min() >= 0.0
                assert valid_data.max() <= 255.0

    # 5. Feature summary validation
    with open(summary_file, "r") as f:
        summary = json.load(f)
    for fname in expected_derived:
        assert fname in summary, f"Missing {fname} in feature_summary.json"
        assert summary[fname]["valid_pixel_count"] > 25000
        assert summary[fname]["min"] is not None
        assert summary[fname]["max"] is not None


def test_real_moil_production_reported():
    from config.settings import settings
    import json
    import pandas as pd

    prod_dir = settings.REAL_DATA_DIR / "moil" / "production"
    prod_csv = prod_dir / "production_reported.csv"
    manifest_file = prod_dir / "source_manifest.json"

    assert prod_csv.exists(), f"Reported production CSV not found at {prod_csv}"
    assert manifest_file.exists(), f"Production source manifest not found at {manifest_file}"

    df = pd.read_csv(prod_csv)
    assert not df.empty, "Reported production dataset is empty"
    assert len(df) >= 20, f"Expected at least 20 reported observations, found {len(df)}"

    required_cols = [
        "period", "period_type", "mine", "company", "state",
        "commodity", "production_tonnes", "grade_percent",
        "source", "source_page", "source_table", "data_status"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing column {col} in production_reported.csv"

    # All data_status must be 'reported'
    assert (df["data_status"] == "reported").all(), "All records must have data_status='reported'"

    # Production tonnes must be positive and realistic
    assert (df["production_tonnes"] > 0).all(), "Found non-positive production tonnage"
    assert df["production_tonnes"].min() >= 50000.0, "Sub-threshold production tonnage"

    # No duplicate observations for same period, period_type, mine, and company
    key_cols = ["period", "period_type", "mine", "company", "state"]
    assert not df.duplicated(subset=key_cols).any(), "Found duplicate production records"

    # Commodity is Manganese Ore
    assert (df["commodity"] == "Manganese Ore").all()

    # Verify source manifest
    with open(manifest_file, "r") as f:
        manifest = json.load(f)
    assert "sources" in manifest
    assert len(manifest["sources"]) >= 5
    for s in manifest["sources"]:
        assert "source_id" in s
        assert "organization" in s
        assert "url" in s


def test_real_moil_production_audit():
    from config.settings import settings
    import pandas as pd

    prod_dir = settings.REAL_DATA_DIR / "moil" / "production"
    audit_csv = prod_dir / "provenance_audit.csv"
    reported_csv = prod_dir / "production_reported.csv"

    assert audit_csv.exists(), f"Provenance audit CSV not found at {audit_csv}"
    assert reported_csv.exists(), f"Reported CSV not found at {reported_csv}"

    audit_df = pd.read_csv(audit_csv)
    reported_df = pd.read_csv(reported_csv)

    assert not audit_df.empty
    assert len(audit_df) == len(reported_df), "Audit count must match reported count"

    expected_cols = [
        "period", "period_type", "current_value_tonnes",
        "verified_value_tonnes", "unit", "match_status",
        "source_organization", "source_document", "source_page",
        "source_table", "source_url", "data_status", "notes"
    ]
    for col in expected_cols:
        assert col in audit_df.columns, f"Missing column {col} in provenance_audit.csv"

    # All match_status must be in allowed set
    allowed_statuses = {"verified", "corrected", "needs_review"}
    assert audit_df["match_status"].isin(allowed_statuses).all()

    # All observations in our dataset are verified
    assert (audit_df["match_status"] == "verified").all()

    # Verified production values must match current values
    assert (audit_df["current_value_tonnes"] == audit_df["verified_value_tonnes"]).all()
    assert (audit_df["verified_value_tonnes"] > 0).all()

    # Metadata columns must be populated
    assert audit_df["source_organization"].notna().all()
    assert audit_df["source_document"].notna().all()
    assert audit_df["source_url"].str.startswith("http").all()
    assert audit_df["notes"].notna().all()


def test_real_feature_grid_dataset_integrity():
    from config.settings import settings
    from src.data.loader import data_loader
    import json

    geo_dir = settings.DERIVED_DATA_DIR / "geospatial" / "balaghat"
    csv_path = geo_dir / "real_feature_grid.csv"
    meta_path = geo_dir / "feature_metadata.json"
    summary_path = geo_dir / "feature_summary.json"
    readme_path = geo_dir / "README.md"
    comp_path = geo_dir / "real_vs_synthetic_feature_comparison.md"

    for p in [csv_path, meta_path, summary_path, readme_path, comp_path]:
        assert p.exists(), f"Expected file missing: {p}"

    # Load through data loader
    df = data_loader.load_real_feature_grid()
    assert len(df) == 27720, "Feature grid should have 27,720 cells"

    # Verify column presence
    required_cols = [
        "cell_id", "x", "y", "longitude", "latitude",
        "B02", "B03", "B04", "B08", "B11", "B12",
        "NDVI", "NDWI", "red_nir_ratio", "swir_nir_ratio",
        "elevation", "slope", "aspect", "hillshade",
        "distance_to_moil_balaghat_m", "valid_feature_fraction", "feature_quality"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"

    # Cell IDs unique
    assert df["cell_id"].nunique() == len(df)
    assert df.duplicated(subset=["x", "y"]).sum() == 0

    # Quality filter test
    valid_df = data_loader.load_real_feature_grid(quality_filter="valid")
    assert len(valid_df) > 27000
    assert (valid_df["valid_feature_fraction"] == 1.0).all()

    # Numerical range checks on valid data
    assert (valid_df["NDVI"] >= -1.0).all() and (valid_df["NDVI"] <= 1.0).all()
    assert (valid_df["NDWI"] >= -1.0).all() and (valid_df["NDWI"] <= 1.0).all()
    assert (valid_df["elevation"] >= 200.0).all() and (valid_df["elevation"] <= 1000.0).all()
    assert (valid_df["slope"] >= 0.0).all() and (valid_df["slope"] <= 90.0).all()
    assert (valid_df["distance_to_moil_balaghat_m"] >= 0.0).all()

    # Coordinates in Balaghat range
    assert valid_df["longitude"].between(80.19, 80.26).all()
    assert valid_df["latitude"].between(21.81, 21.88).all()

    # Verify metadata JSON
    with open(meta_path, "r") as f:
        meta = json.load(f)
    assert meta["data_status"] == "derived"
    assert meta["grid_resolution_m"] == 30.0
    assert meta["aoi"]["total_cells"] == 27720

    # Verify feature summary JSON
    with open(summary_path, "r") as f:
        summary = json.load(f)
    assert summary["total_cells"] == 27720
    assert "elevation" in summary["numerical_features"]
    assert "NDVI" in summary["numerical_features"]


def test_mineralization_evidence_and_provenance_audit():
    from config.settings import settings
    import pandas as pd

    geo_dir = settings.REAL_DATA_DIR / "geology" / "balaghat"
    derived_geo = settings.DERIVED_DATA_DIR / "geospatial" / "balaghat"

    evid_csv = geo_dir / "mineralization_evidence.csv"
    audit_csv = geo_dir / "mineralization_provenance_audit.csv"
    report_md = geo_dir / "phase9a_report.md"
    label_csv = derived_geo / "mineralization_label_candidates.csv"

    for p in [evid_csv, audit_csv, report_md, label_csv]:
        assert p.exists(), f"Missing required file: {p}"

    # 1. Evidence Registry Tests
    df_evid = pd.read_csv(evid_csv)
    assert len(df_evid) >= 10, "Should have at least 10 authoritative records"
    assert df_evid["evidence_id"].nunique() == len(df_evid), "Evidence IDs must be unique"
    assert (df_evid["commodity"] == "Manganese Ore").all(), "All commodities must be verified Manganese Ore"
    assert df_evid["source_url"].str.startswith("http").all(), "All sources must have authoritative URLs"

    # Coordinates in Central India Manganese Belt bounds
    assert df_evid["latitude"].between(21.0, 22.5).all()
    assert df_evid["longitude"].between(78.5, 81.0).all()

    # Allowed label eligibilities
    allowed_eligibilities = {"strong_positive_candidate", "weak_positive_candidate", "context_only", "not_usable"}
    assert df_evid["label_eligibility"].isin(allowed_eligibilities).all()

    # 2. Provenance Audit Tests
    df_audit = pd.read_csv(audit_csv)
    assert len(df_audit) == len(df_evid)
    assert (df_audit["source_verified"] == True).all()
    assert (df_audit["commodity_verified"] == True).all()
    assert "inside_balaghat_aoi" in df_audit.columns

    # 3. Candidate Label Integrity
    df_labels = pd.read_csv(label_csv)
    assert len(df_labels) == 27720, "Must cover all 27,720 cells"
    
    # Verify no synthetic negative labels exist
    assert "negative_candidate" not in df_labels["label_candidate"].values, "Must NOT contain pseudo-negatives"
    
    # Verified counts
    val_counts = df_labels["label_candidate"].value_counts().to_dict()
    assert val_counts.get("positive_candidate", 0) == 1, "Only exact surveyed shaft portal is strong positive"
    assert val_counts.get("weak_positive_candidate", 0) == 34, "Proximal surface pit footprint (excluding portal)"
    assert val_counts.get("unlabeled", 0) == 27685, "All unevidenced cells must remain strictly unlabeled"







