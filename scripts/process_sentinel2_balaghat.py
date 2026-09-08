"""
Sentinel-2 Level-2A Processing Pipeline for Balaghat Mine (MOIL) AOI
Acquires real Sentinel-2 COG bands via public AWS Earth Search / Open Data STAC,
crops to a 5 km x 5 km AOI around audited MOIL Balaghat coordinates,
and calculates analytical remote-sensing features (NDVI, NDWI, ratios).
"""

import json
import os
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.transform import from_bounds as transform_from_bounds
from rasterio.enums import Resampling
from pyproj import Transformer
from PIL import Image

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
REAL_S2_DIR = BASE_DIR / "data" / "real" / "sentinel2" / "balaghat"
RAW_S2_DIR = REAL_S2_DIR / "raw"
DERIVED_S2_DIR = BASE_DIR / "data" / "derived" / "sentinel2" / "balaghat"

for d in [REAL_S2_DIR, RAW_S2_DIR, DERIVED_S2_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Audited Anchor: MOIL_BALAGHAT (Lon: 80.2281, Lat: 21.8464)
CENTER_LON = 80.2281
CENTER_LAT = 21.8464
# 5 km x 5 km bounding box (~0.048 deg lon, ~0.045 deg lat)
DELTA_LON = 0.0242
DELTA_LAT = 0.0225

MIN_LON = round(CENTER_LON - DELTA_LON, 4)
MAX_LON = round(CENTER_LON + DELTA_LON, 4)
MIN_LAT = round(CENTER_LAT - DELTA_LAT, 4)
MAX_LAT = round(CENTER_LAT + DELTA_LAT, 4)

# 1. Create AOI GeoJSON
aoi_geojson = {
    "type": "FeatureCollection",
    "name": "MOIL_Balaghat_Sentinel2_AOI",
    "crs": {
        "type": "name",
        "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
    },
    "features": [
        {
            "type": "Feature",
            "properties": {
                "aoi_name": "Balaghat Mine 5km x 5km AOI",
                "anchor_mine_id": "MOIL_BALAGHAT",
                "anchor_mine_name": "Balaghat (Bharweli)",
                "center_wgs84": [CENTER_LON, CENTER_LAT],
                "bbox_wgs84": [MIN_LON, MIN_LAT, MAX_LON, MAX_LAT],
                "width_km": 5.0,
                "height_km": 5.0,
                "purpose": "Phase 3 Real Remote-Sensing Baseline Acquisition"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [MIN_LON, MIN_LAT],
                        [MAX_LON, MIN_LAT],
                        [MAX_LON, MAX_LAT],
                        [MIN_LON, MAX_LAT],
                        [MIN_LON, MIN_LAT]
                    ]
                ]
            }
        }
    ]
}

with open(REAL_S2_DIR / "aoi.geojson", "w") as f:
    json.dump(aoi_geojson, f, indent=2)
print("Saved aoi.geojson")

# Sentinel-2 Scene Info (Cloud-free Level-2A)
SCENE_ID = "S2A_44QMK_20240417_0_L2A"
S2_COG_BASE = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/44/Q/MK/2024/4/S2A_44QMK_20240417_0_L2A"

BAND_ASSETS = {
    "B02": {"name": "Blue", "url": f"{S2_COG_BASE}/B02.tif", "native_res": 10},
    "B03": {"name": "Green", "url": f"{S2_COG_BASE}/B03.tif", "native_res": 10},
    "B04": {"name": "Red", "url": f"{S2_COG_BASE}/B04.tif", "native_res": 10},
    "B08": {"name": "NIR", "url": f"{S2_COG_BASE}/B08.tif", "native_res": 10},
    "B11": {"name": "SWIR1", "url": f"{S2_COG_BASE}/B11.tif", "native_res": 20},
    "B12": {"name": "SWIR2", "url": f"{S2_COG_BASE}/B12.tif", "native_res": 20},
    "TCI": {"name": "TrueColor", "url": f"{S2_COG_BASE}/TCI.tif", "native_res": 10},
}

cropped_bands = {}
reference_meta = None

# Download & crop each band
for band_id, info in BAND_ASSETS.items():
    raw_out = RAW_S2_DIR / f"{band_id}.tif"
    print(f"Fetching {band_id} ({info['name']})...")
    with rasterio.open(info["url"]) as src:
        transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        min_x, min_y = transformer.transform(MIN_LON, MIN_LAT)
        max_x, max_y = transformer.transform(MAX_LON, MAX_LAT)
        window = from_bounds(min_x, min_y, max_x, max_y, src.transform)

        data = src.read(window=window)
        win_transform = src.window_transform(window)
        meta = src.meta.copy()
        meta.update({
            "height": data.shape[1],
            "width": data.shape[2],
            "transform": win_transform,
            "driver": "GTiff"
        })

        with rasterio.open(raw_out, "w", **meta) as dst:
            dst.write(data)

        cropped_bands[band_id] = {
            "data": data,
            "meta": meta,
            "native_res": info["native_res"]
        }
        if band_id == "B04":
            reference_meta = meta

print("All raw AOI bands saved to data/real/sentinel2/balaghat/raw/")

# Prepare analytical 10m arrays (reflectance scale 0-10000 -> 0.0-1.0)
ref_height = cropped_bands["B04"]["data"].shape[1]
ref_width = cropped_bands["B04"]["data"].shape[2]

b2 = cropped_bands["B02"]["data"][0].astype(np.float32) / 10000.0
b3 = cropped_bands["B03"]["data"][0].astype(np.float32) / 10000.0
b4 = cropped_bands["B04"]["data"][0].astype(np.float32) / 10000.0
b8 = cropped_bands["B08"]["data"][0].astype(np.float32) / 10000.0

# Resample B11 (20m) to reference 10m grid using bilinear interpolation
with rasterio.open(RAW_S2_DIR / "B11.tif") as src:
    b11_resampled = src.read(
        1,
        out_shape=(ref_height, ref_width),
        resampling=Resampling.bilinear
    ).astype(np.float32) / 10000.0

# Compute Indices
# 1. NDVI = (NIR - RED) / (NIR + RED)
denom_ndvi = b8 + b4
ndvi = np.where(denom_ndvi > 0, (b8 - b4) / denom_ndvi, np.nan).astype(np.float32)
ndvi = np.clip(ndvi, -1.0, 1.0)

# 2. NDWI (McFeeters 1996 formulation: (Green - NIR) / (Green + NIR))
denom_ndwi = b3 + b8
ndwi = np.where(denom_ndwi > 0, (b3 - b8) / denom_ndwi, np.nan).astype(np.float32)
ndwi = np.clip(ndwi, -1.0, 1.0)

# 3. Red / NIR Ratio = B04 / B08
red_nir = np.where(b8 > 0.001, b4 / b8, np.nan).astype(np.float32)

# 4. SWIR / NIR Ratio = B11 / B08
swir_nir = np.where(b8 > 0.001, b11_resampled / b8, np.nan).astype(np.float32)

# Save Derived GeoTIFFs
derived_layers = {
    "ndvi.tif": ndvi,
    "ndwi.tif": ndwi,
    "red_nir_ratio.tif": red_nir,
    "swir_nir_ratio.tif": swir_nir,
}

feat_meta = reference_meta.copy()
feat_meta.update({
    "count": 1,
    "dtype": "float32",
    "nodata": -9999.0
})

feature_summary = {}

for filename, arr in derived_layers.items():
    out_path = DERIVED_S2_DIR / filename
    clean_arr = np.nan_to_num(arr, nan=-9999.0)
    with rasterio.open(out_path, "w", **feat_meta) as dst:
        dst.write(clean_arr, 1)

    valid_mask = ~np.isnan(arr) & (arr != -9999.0)
    valid_pixels = arr[valid_mask]
    feature_summary[filename] = {
        "valid_pixel_count": int(valid_mask.sum()),
        "nodata_pixel_count": int((~valid_mask).sum()),
        "min": float(np.min(valid_pixels)) if len(valid_pixels) else None,
        "max": float(np.max(valid_pixels)) if len(valid_pixels) else None,
        "mean": float(np.mean(valid_pixels)) if len(valid_pixels) else None,
        "median": float(np.median(valid_pixels)) if len(valid_pixels) else None,
        "std": float(np.std(valid_pixels)) if len(valid_pixels) else None,
    }

feature_summary["metadata"] = {
    "scene_id": SCENE_ID,
    "acquisition_date": "2024-04-17",
    "aoi_dimensions_pixels": [int(ref_height), int(ref_width)],
    "grid_resolution_m": 10.0,
    "formulas": {
        "ndvi": "(B08_NIR - B04_RED) / (B08_NIR + B04_RED)",
        "ndwi": "(B03_GREEN - B08_NIR) / (B03_GREEN + B08_NIR) [McFeeters 1996]",
        "red_nir_ratio": "B04_RED / B08_NIR",
        "swir_nir_ratio": "B11_SWIR1 / B08_NIR (B11 bilinearly resampled 20m -> 10m)"
    }
}

with open(DERIVED_S2_DIR / "feature_summary.json", "w") as f:
    json.dump(feature_summary, f, indent=2)
print("Saved derived GeoTIFFs and feature_summary.json")

# Generate Visual Products (true_color.png and ndvi.png)
# True Color RGB: B04, B03, B02 (scaled 2nd to 98th percentile to 0-255)
rgb = np.stack([b4, b3, b2], axis=-1)
p2, p98 = np.percentile(rgb, (2, 98))
rgb_scaled = np.clip((rgb - p2) / (p98 - p2), 0, 1)
rgb_8bit = (rgb_scaled * 255).astype(np.uint8)
img_rgb = Image.fromarray(rgb_8bit)
img_rgb.save(DERIVED_S2_DIR / "true_color.png")

# NDVI color ramp (Grayscale to contrast-stretched RGB for visualization)
ndvi_norm = np.clip((ndvi - (-0.2)) / (0.8 - (-0.2)), 0, 1)
ndvi_8bit = (ndvi_norm * 255).astype(np.uint8)
# Apply a green-amber-blue color palette
pal = []
for i in range(256):
    norm = i / 255.0
    if norm < 0.35: # Water / Bare / Excavation
        r, g, b = int(180 * (1 - norm / 0.35)), int(120 * (1 - norm / 0.35)), int(220)
    elif norm < 0.65: # Low vegetation / soil
        t = (norm - 0.35) / 0.30
        r, g, b = int(180 + 40 * t), int(160 + 50 * t), int(50)
    else: # Dense vegetation / canopy
        t = (norm - 0.65) / 0.35
        r, g, b = int(40 * (1 - t)), int(160 + 80 * t), int(40)
    pal.extend([r, g, b])

img_ndvi = Image.fromarray(ndvi_8bit, mode="P")
img_ndvi.putpalette(pal)
img_ndvi.convert("RGB").save(DERIVED_S2_DIR / "ndvi.png")
print("Saved true_color.png and ndvi.png")

# Save Metadata JSON
metadata = {
    "source": "Copernicus Sentinel-2 Level-2A (via AWS Earth Search / Open Data STAC)",
    "provider": "European Space Agency (ESA) / AWS Open Data",
    "product_id": SCENE_ID,
    "satellite": "Sentinel-2A",
    "acquisition_date": "2024-04-17T05:22:46.341000Z",
    "processing_level": "Level-2A (Bottom-of-Atmosphere Surface Reflectance)",
    "cloud_cover_pct": 0.000325,
    "aoi": {
        "target": "MOIL_BALAGHAT",
        "center_wgs84": [CENTER_LON, CENTER_LAT],
        "bbox_wgs84": [MIN_LON, MIN_LAT, MAX_LON, MAX_LAT],
        "dimensions_km": [5.0, 5.0]
    },
    "bands": [
        {"band": "B02", "name": "Blue", "wavelength_nm": 492.4, "native_resolution_m": 10, "source_url": BAND_ASSETS["B02"]["url"]},
        {"band": "B03", "name": "Green", "wavelength_nm": 559.8, "native_resolution_m": 10, "source_url": BAND_ASSETS["B03"]["url"]},
        {"band": "B04", "name": "Red", "wavelength_nm": 664.6, "native_resolution_m": 10, "source_url": BAND_ASSETS["B04"]["url"]},
        {"band": "B08", "name": "NIR", "wavelength_nm": 832.8, "native_resolution_m": 10, "source_url": BAND_ASSETS["B08"]["url"]},
        {"band": "B11", "name": "SWIR1", "wavelength_nm": 1610.4, "native_resolution_m": 20, "source_url": BAND_ASSETS["B11"]["url"], "resampling_for_analysis": "Bilinear interpolation to 10m reference grid"},
        {"band": "B12", "name": "SWIR2", "wavelength_nm": 2185.7, "native_resolution_m": 20, "source_url": BAND_ASSETS["B12"]["url"], "resampling_for_analysis": "None (preserved at native 20m in raw/)"},
        {"band": "TCI", "name": "True Color Image (RGB)", "native_resolution_m": 10, "source_url": BAND_ASSETS["TCI"]["url"]}
    ],
    "crs": "EPSG:32644 (UTM Zone 44N)",
    "resolution_m": 10.0,
    "download_date": "2026-09-06",
    "processing_steps": [
        "Identified lowest cloud-cover Level-2A acquisition for Balaghat AOI via STAC search (cloud cover 0.0003%).",
        "Performed windowed HTTP range read from Cloud-Optimized GeoTIFFs (COGs) for 5 km x 5 km bounding box.",
        "Saved cropped raw bands (B02, B03, B04, B08, B11, B12, TCI) to data/real/sentinel2/balaghat/raw/.",
        "Scaled raw digital numbers (DN) to surface reflectance (DN / 10000.0).",
        "Resampled 20m SWIR1 band (B11) to 10m reference grid using bilinear interpolation.",
        "Computed NDVI: (B08 - B04) / (B08 + B04).",
        "Computed NDWI: (B03 - B08) / (B03 + B08) [McFeeters 1996].",
        "Computed spectral ratios: Red/NIR (B04/B08) and SWIR1/NIR (B11/B08).",
        "Exported single-band analytical GeoTIFFs to data/derived/sentinel2/balaghat/.",
        "Generated diagnostic true_color.png and ndvi.png visualizations."
    ],
    "credentials_required": False,
    "scientific_disclaimer": "NDVI, NDWI, and spectral ratios represent real remote-sensing surface reflectance indices. They are NOT classified as proven manganese mineralization indicators at this stage."
}

with open(REAL_S2_DIR / "metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
print("Saved metadata.json")
