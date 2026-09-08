"""
DEM Processing Pipeline for Balaghat Mine (MOIL) AOI
Acquires Copernicus DEM GLO-30 (30m global digital surface model) via AWS Open Data COG,
clips to the 5 km x 5 km Balaghat AOI, reprojects to UTM Zone 44N (EPSG:32644),
and derives terrain features: elevation, slope, aspect, and analytical hillshade.
"""

import json
from pathlib import Path
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.windows import from_bounds
from pyproj import Transformer
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
REAL_DEM_DIR = BASE_DIR / "data" / "real" / "dem" / "balaghat"
RAW_DEM_DIR = REAL_DEM_DIR / "raw"
DERIVED_DEM_DIR = BASE_DIR / "data" / "derived" / "dem" / "balaghat"

for d in [REAL_DEM_DIR, RAW_DEM_DIR, DERIVED_DEM_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 1. Load Existing AOI from Sentinel-2
with open(BASE_DIR / "data" / "real" / "sentinel2" / "balaghat" / "aoi.geojson", "r") as f:
    aoi_geojson = json.load(f)

# Save copy in dem directory
with open(REAL_DEM_DIR / "aoi.geojson", "w") as f:
    json.dump(aoi_geojson, f, indent=2)

feat_props = aoi_geojson["features"][0]["properties"]
coords = aoi_geojson["features"][0]["geometry"]["coordinates"][0]
min_lon = min(c[0] for c in coords)
max_lon = max(c[0] for c in coords)
min_lat = min(c[1] for c in coords)
max_lat = max(c[1] for c in coords)

print(f"Balaghat AOI bounds (WGS84): Lon [{min_lon}, {max_lon}], Lat [{min_lat}, {max_lat}]")

# 2. Copernicus DEM GLO-30 Source
DEM_TILE_ID = "Copernicus_DSM_COG_10_N21_00_E080_00_DEM"
DEM_COG_URL = f"https://copernicus-dem-30m.s3.amazonaws.com/{DEM_TILE_ID}/{DEM_TILE_ID}.tif"

raw_dem_path = RAW_DEM_DIR / "copernicus_dem_30m_balaghat.tif"

print(f"Fetching raw DEM tile subset from {DEM_COG_URL}...")
with rasterio.open(DEM_COG_URL) as src:
    win = from_bounds(min_lon, min_lat, max_lon, max_lat, src.transform)
    raw_data = src.read(1, window=win)
    win_transform = src.window_transform(win)
    raw_meta = src.meta.copy()
    raw_meta.update({
        "height": raw_data.shape[0],
        "width": raw_data.shape[1],
        "transform": win_transform,
        "driver": "GTiff",
        "nodata": -9999.0
    })

    with rasterio.open(raw_dem_path, "w", **raw_meta) as dst:
        dst.write(raw_data.astype(np.float32), 1)

print(f"Saved raw DEM ({raw_data.shape[0]}x{raw_data.shape[1]}) to {raw_dem_path}")

# 3. Reproject DEM to Projected UTM Zone 44N (EPSG:32644) for Metric Terrain Analysis
# Target resolution: 30.0 meters in UTM Zone 44N (preserving native 1 arc-second scale)
dst_crs = "EPSG:32644"
target_res = 30.0

with rasterio.open(raw_dem_path) as src:
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds, resolution=target_res
    )
    proj_meta = src.meta.copy()
    proj_meta.update({
        "crs": dst_crs,
        "transform": transform,
        "width": width,
        "height": height,
        "nodata": -9999.0,
        "dtype": "float32"
    })

    elev_proj = np.empty((height, width), dtype=np.float32)
    reproject(
        source=rasterio.band(src, 1),
        destination=elev_proj,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=transform,
        dst_crs=dst_crs,
        resampling=Resampling.bilinear,
        dst_nodata=-9999.0
    )

# 4. Calculate Terrain Derivatives using Horn's Method (3x3 Kernel)
# Cell dimensions in meters: dx = target_res, dy = target_res
dx = target_res
dy = target_res

# Pad elevation boundary using reflection for gradient calculation
elev_pad = np.pad(elev_proj, 1, mode="reflect")

# Horn's partial derivatives
dz_dx = ((elev_pad[:-2, 2:] + 2 * elev_pad[1:-1, 2:] + elev_pad[2:, 2:]) -
         (elev_pad[:-2, :-2] + 2 * elev_pad[1:-1, :-2] + elev_pad[2:, :-2])) / (8.0 * dx)

dz_dy = ((elev_pad[:-2, :-2] + 2 * elev_pad[:-2, 1:-1] + elev_pad[:-2, 2:]) -
         (elev_pad[2:, :-2] + 2 * elev_pad[2:, 1:-1] + elev_pad[2:, 2:])) / (8.0 * dy)

# 4a. Slope in Degrees [0 to 90]
slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
slope_deg = np.rad2deg(slope_rad).astype(np.float32)

# 4b. Aspect in Degrees [0 to 360, where 0/360 = North, 90 = East, 180 = South, 270 = West]
# Flat areas (slope < 0.1 deg) assigned -1.0
aspect_rad = np.arctan2(dz_dy, -dz_dx)
aspect_deg = 90.0 - np.rad2deg(aspect_rad)
aspect_deg = np.where(aspect_deg < 0.0, aspect_deg + 360.0, aspect_deg)
aspect_deg = np.where(aspect_deg >= 360.0, aspect_deg - 360.0, aspect_deg)
aspect_deg = np.where(slope_deg < 0.1, -1.0, aspect_deg).astype(np.float32)

# 4c. Analytical Hillshade [0 to 255]
# Standard Illumination: Azimuth 315 deg (NW), Altitude 45 deg (Zenith 45 deg)
sun_azimuth_rad = np.deg2rad(315.0)
sun_zenith_rad = np.deg2rad(45.0)

hillshade = 255.0 * (
    np.cos(sun_zenith_rad) * np.cos(slope_rad) +
    np.sin(sun_zenith_rad) * np.sin(slope_rad) * np.cos(sun_azimuth_rad - np.deg2rad(np.where(aspect_deg < 0, 0, aspect_deg)))
)
hillshade = np.clip(hillshade, 0.0, 255.0).astype(np.float32)

# 4d. Propagate Nodata Mask from Projected Elevation
nodata_mask = (elev_proj == -9999.0) | np.isnan(elev_proj)
slope_deg[nodata_mask] = -9999.0
aspect_deg[nodata_mask] = -9999.0
hillshade[nodata_mask] = -9999.0

# 5. Write Derived GeoTIFFs
derived_outputs = {
    "elevation.tif": (elev_proj, "meters above sea level (EGM2008)"),
    "slope.tif": (slope_deg, "degrees (0-90)"),
    "aspect.tif": (aspect_deg, "degrees (0-360, flat = -1)"),
    "hillshade.tif": (hillshade, "shaded relief intensity (0-255)"),
}

feature_summary = {}

for fname, (arr, units) in derived_outputs.items():
    out_file = DERIVED_DEM_DIR / fname
    with rasterio.open(out_file, "w", **proj_meta) as dst:
        dst.write(arr, 1)

    valid_mask = (arr != -9999.0) & ~np.isnan(arr)
    # For aspect, exclude flat -1 values when reporting directional circular statistics
    stat_mask = valid_mask if fname != "aspect.tif" else valid_mask & (arr >= 0.0)
    stat_pixels = arr[stat_mask]

    feature_summary[fname] = {
        "units": units,
        "valid_pixel_count": int(valid_mask.sum()),
        "nodata_pixel_count": int((~valid_mask).sum()),
        "min": float(np.min(stat_pixels)) if len(stat_pixels) else None,
        "max": float(np.max(stat_pixels)) if len(stat_pixels) else None,
        "mean": float(np.mean(stat_pixels)) if len(stat_pixels) else None,
        "median": float(np.median(stat_pixels)) if len(stat_pixels) else None,
        "std": float(np.std(stat_pixels)) if len(stat_pixels) else None,
    }

feature_summary["metadata"] = {
    "dem_source": "Copernicus DEM GLO-30 (ESA / Airbus / AWS Open Data)",
    "tile_id": DEM_TILE_ID,
    "grid_resolution_m": target_res,
    "grid_dimensions": [int(height), int(width)],
    "crs": dst_crs,
    "nodata_value": -9999.0,
    "vertical_datum": "EGM2008 Geoid",
    "formulas": {
        "slope": "arctan(sqrt((dz/dx)^2 + (dz/dy)^2)) * 180 / pi [Horn's 3x3 method]",
        "aspect": "(90 - arctan2(dz/dy, -dz/dx) * 180 / pi) mod 360 [flat cells = -1]",
        "hillshade": "255 * (cos(zenith)*cos(slope) + sin(zenith)*sin(slope)*cos(azimuth - aspect)) [Azimuth=315 deg, Altitude=45 deg]"
    }
}

with open(DERIVED_DEM_DIR / "feature_summary.json", "w") as f:
    json.dump(feature_summary, f, indent=2)
print("Saved derived GeoTIFFs and feature_summary.json")

# 6. Save Metadata JSON in data/real/dem/balaghat/metadata.json
metadata = {
    "provider": "European Space Agency (ESA) & Airbus Defence and Space under the Copernicus Programme",
    "dataset_name": "Copernicus Digital Elevation Model GLO-30",
    "dataset_version": "GLO-30 (Public 30-meter Global DEM)",
    "tile_name": DEM_TILE_ID,
    "source_url": "https://registry.opendata.aws/copernicus-dem/",
    "download_url": DEM_COG_URL,
    "access_method": "Windowed Cloud-Optimized GeoTIFF (COG) HTTP range read via AWS Open Data",
    "credentials_required": False,
    "native_crs": "EPSG:4326 (WGS84)",
    "native_resolution": "1 arc-second (~30 meters, 0.00027778 degrees)",
    "processing_crs": "EPSG:32644 (UTM Zone 44N)",
    "processing_resolution_m": 30.0,
    "vertical_units": "meters",
    "vertical_datum": "EGM2008 Geoid",
    "horizontal_units": "meters (projected UTM)",
    "nodata_value": -9999.0,
    "aoi": {
        "target": "MOIL_BALAGHAT",
        "center_wgs84": [80.2281, 21.8464],
        "bbox_wgs84": [min_lon, min_lat, max_lon, max_lat],
        "dimensions_km": [5.0, 5.0]
    },
    "bhuvan_cartodem_investigation": "ISRO Bhuvan NRSC CartoDEM was investigated as the primary Indian national candidate. Automated API access is restricted on bhuvan-app1.nrsc.gov.in (requires interactive Indian mobile SMS OTP authentication and Captcha session). Copernicus DEM GLO-30 was selected as the verified, zero-credential authoritative 30m public alternative.",
    "scientific_disclaimer": "These terrain layers (elevation, slope, aspect, hillshade) represent real physical topographical measurements. They are NOT, by themselves, evidence of manganese mineralization."
}

with open(REAL_DEM_DIR / "metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
print("Saved metadata.json")
