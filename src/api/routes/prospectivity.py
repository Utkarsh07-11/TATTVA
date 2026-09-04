"""Geospatial prospectivity and resource endpoints."""

import json
from typing import Dict, Any
from fastapi import APIRouter, Query

from config.settings import settings
from src.api.deps import get_prospectivity_model
from src.data.loader import data_loader
from src.geospatial.kriging import GeostatisticalResourceEstimator

router = APIRouter(prefix="/prospectivity", tags=["Geospatial & Reserve Intelligence"])


@router.get("/map")
def get_prospectivity_map(mine_id: str = Query("MOIL_01")) -> Dict[str, Any]:
    surface_file = settings.PROCESSED_DATA_DIR / "prospectivity_surface.geojson"
    if surface_file.exists():
        with open(surface_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
            payload.setdefault("metadata", {})
            payload["metadata"]["mine_id"] = mine_id
            return payload

    model = get_prospectivity_model()
    sat_df = data_loader.load_satellite_grid()
    scored_grid = model.predict_grid_surface(sat_df)
    return model.to_geojson_feature_collection(scored_grid)


@router.get("/drillholes")
def get_drillholes() -> Dict[str, Any]:
    dh_df = data_loader.load_drillhole_assay()
    features = []
    for _, row in dh_df.iterrows():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row["longitude"]), float(row["latitude"])],
            },
            "properties": {
                "hole_id": row["hole_id"],
                "collar_elevation_m": float(row["collar_elevation_m"]),
                "total_depth_m": float(row["total_depth_m"]),
                "depth_from_m": float(row["depth_from_m"]),
                "depth_to_m": float(row["depth_to_m"]),
                "thickness_m": float(row["thickness_m"]),
                "mn_grade_pct": float(row["mn_grade_pct"]),
                "fe_grade_pct": float(row["fe_grade_pct"]),
                "sio2_pct": float(row["sio2_pct"]),
                "lithology_code": row["lithology_code"],
                "sample_date": str(row["sample_date"]),
                "structural_domain": row["structural_domain"],
                "is_ore_bearing": int(row["is_ore_bearing"]),
            },
        })

    return {
        "type": "FeatureCollection",
        "metadata": {
            "total_drillholes": len(features),
            "region": "Central Indian Manganese Belt (Sausar Group / Balaghat)",
            "disclaimer": "Ground-truth collar assays and geological logs.",
        },
        "features": features,
    }


@router.get("/resource-estimate")
def get_resource_estimate(cutoff_grade_pct: float = Query(20.0, ge=10.0, le=40.0)) -> Dict[str, Any]:
    dh_df = data_loader.load_drillhole_assay()
    sat_df = data_loader.load_satellite_grid()
    idw_df = GeostatisticalResourceEstimator.inverse_distance_weighting(dh_df, sat_df)
    return GeostatisticalResourceEstimator.estimate_resource_summary(idw_df, cutoff_grade_pct=cutoff_grade_pct)
