"""
Data Validation Engine for SIH 2026 PS 26009
Ensures schema adherence, value range constraints, absence of unhandled nulls,
and verifies statutory / DSR source-derived data integrity and coordinate validity.
Phase 15.1: Rigorous Provenance & Projected Metric CRS Geometry Validation.
"""

from typing import Tuple, List, Dict, Any, Optional
import math
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from rasterio.warp import transform


class DailyProductionRecord(BaseModel):
    date: str
    mine_block_id: str
    planned_tonnes: float = Field(ge=0.0, le=5000.0)
    actual_tonnes: float = Field(ge=0.0, le=5000.0)
    equipment_availability_pct: float = Field(ge=0.0, le=100.0)
    rainfall_mm: float = Field(ge=0.0, le=500.0)
    blasting_delay_flag: int = Field(ge=0, le=1)
    maintenance_flag: int = Field(ge=0, le=1)
    synthetic: bool


class DrillholeAssayRecord(BaseModel):
    hole_id: str
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    collar_elevation_m: float
    total_depth_m: float = Field(gt=0.0)
    depth_from_m: float = Field(ge=0.0)
    depth_to_m: float = Field(gt=0.0)
    thickness_m: float = Field(gt=0.0)
    mn_grade_pct: float = Field(ge=0.0, le=100.0)
    fe_grade_pct: float = Field(ge=0.0, le=100.0)
    sio2_pct: float = Field(ge=0.0, le=100.0)
    lithology_code: str
    sample_date: str
    is_ore_bearing: int = Field(ge=0, le=1)
    source: str


class SatelliteGridRecord(BaseModel):
    grid_id: str
    latitude: float
    longitude: float
    elevation_m: float
    slope_deg: float = Field(ge=0.0, le=90.0)
    aspect_deg: float = Field(ge=0.0, le=360.0)
    ndvi: float = Field(ge=-1.0, le=1.0)
    ndwi: float = Field(ge=-1.0, le=1.0)
    iron_oxide_index: float = Field(ge=0.0)
    clay_index: float = Field(ge=0.0)
    ferrous_index: float = Field(ge=0.0)
    lst_k: float = Field(gt=200.0, lt=360.0)
    synthetic: bool


VALID_PROVENANCE_CATEGORIES = {
    "REAL / SURVEYED",
    "REAL",
    "SOURCE-DERIVED",
    "SOURCE-DERIVED / PARTIAL",
    "DERIVED",
    "REFERENCE",
    "SIMULATION",
    "EXPERIMENTAL",
    "UNAVAILABLE"
}

VALID_POINT_TYPES = {
    "mine_site_reference",
    "shaft_portal",
    "lease_centroid",
    "boundary_centroid",
    "boundary_pillar",
    "statutory_point",
    "outcrop_strike_center",
    "administrative_reference"
}


class DataValidator:
    """Validates loaded Pandas DataFrames against engineering, geological, and DSR statutory constraints."""

    @staticmethod
    def calculate_projected_polygon_area_ha(
        coordinates_wgs84: List[List[float]],
        src_crs: str = "EPSG:4326",
        dst_crs: str = "EPSG:32644"
    ) -> float:
        """
        Calculates exact planar polygon area in hectares on a projected metric CRS (e.g. UTM Zone 44N EPSG:32644).
        Applies the metric Shoelace formula to projected coordinates.
        Does NOT rely on rough spherical/degree approximations.
        """
        if len(coordinates_wgs84) < 4:
            raise ValueError("Polygon requires at least 4 coordinate vertices (including closure).")

        lons = [pt[0] for pt in coordinates_wgs84]
        lats = [pt[1] for pt in coordinates_wgs84]

        # Project coordinates from WGS84 to metric UTM Zone 44N
        xs, ys = transform(src_crs, dst_crs, lons, lats)

        # Shoelace formula on metric meters
        area_m2 = 0.5 * abs(sum(xs[i] * ys[i + 1] - xs[i + 1] * ys[i] for i in range(len(xs) - 1)))
        area_ha = area_m2 / 10000.0
        return float(area_ha)

    @staticmethod
    def validate_production(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        required_cols = [
            "date", "mine_block_id", "planned_tonnes", "actual_tonnes",
            "equipment_availability_pct", "rainfall_mm", "blasting_delay_flag", "maintenance_flag"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            errors.append(f"Missing required columns in production data: {missing}")
            return False, errors

        if df["actual_tonnes"].isnull().any():
            errors.append("Null values detected in 'actual_tonnes'")
        if (df["equipment_availability_pct"] < 0).any() or (df["equipment_availability_pct"] > 100).any():
            errors.append("equipment_availability_pct outside valid range [0, 100]")
        if (df["rainfall_mm"] < 0).any():
            errors.append("Negative rainfall values detected")

        return len(errors) == 0, errors

    @staticmethod
    def validate_drillholes(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        required_cols = [
            "hole_id", "latitude", "longitude", "mn_grade_pct", "lithology_code", "is_ore_bearing"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            errors.append(f"Missing required columns in drillhole data: {missing}")
            return False, errors

        if (df["mn_grade_pct"] < 0.0).any() or (df["mn_grade_pct"] > 100.0).any():
            errors.append("mn_grade_pct outside [0, 100]")
        if df["hole_id"].duplicated().any():
            errors.append("Duplicate hole_ids detected")

        return len(errors) == 0, errors

    @staticmethod
    def validate_satellite_grid(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        required_cols = [
            "grid_id", "latitude", "longitude", "ndvi", "ndwi", "iron_oxide_index", "clay_index", "elevation_m"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            errors.append(f"Missing required columns in satellite grid data: {missing}")
            return False, errors

        if (df["ndvi"] < -1.0).any() or (df["ndvi"] > 1.0).any():
            errors.append("NDVI outside [-1, 1]")
        if (df["slope_deg"] < 0.0).any() or (df["slope_deg"] > 90.0).any():
            errors.append("Slope degrees outside [0, 90]")

        return len(errors) == 0, errors

    # --- DSR 2022 Statutory & Source-Derived Validators ---

    @staticmethod
    def validate_dsr_mine_registry(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        required_cols = [
            "mine_id", "mine_name", "company", "state", "district",
            "tehsil", "lease_area_ha", "operating_status", "mining_method",
            "latitude", "longitude", "point_type", "data_status", "provenance_status"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            errors.append(f"Missing required columns in DSR mine registry: {missing}")
            return False, errors

        if df["mine_id"].duplicated().any():
            errors.append("Duplicate mine_ids detected in DSR mine registry")
        if not df["latitude"].between(20.0, 24.0).all():
            errors.append("Latitude coordinates outside valid Central India region [20.0, 24.0]")
        if not df["longitude"].between(78.0, 82.0).all():
            errors.append("Longitude coordinates outside valid Central India region [78.0, 82.0]")
        if (df["lease_area_ha"] <= 0).any():
            errors.append("Non-positive lease_area_ha detected")

        invalid_pts = df[~df["point_type"].isin(VALID_POINT_TYPES)]["point_type"].tolist()
        if invalid_pts:
            errors.append(f"Invalid point_type values: {invalid_pts}")

        if "provenance_category" in df.columns:
            invalid_prov = df[~df["provenance_category"].isin(VALID_PROVENANCE_CATEGORIES)]["provenance_category"].tolist()
            if invalid_prov:
                errors.append(f"Invalid provenance_category values: {invalid_prov}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_dsr_lease_areas(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        required_cols = [
            "lease_id", "mine_id", "mine_name", "forest_area_ha",
            "non_forest_area_ha", "total_lease_area_ha", "source_name"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            errors.append(f"Missing required columns in lease areas: {missing}")
            return False, errors

        if (df["total_lease_area_ha"] <= 0).any():
            errors.append("Non-positive total_lease_area_ha detected")
        if (df["forest_area_ha"] < 0).any() or (df["non_forest_area_ha"] < 0).any():
            errors.append("Negative forest/non-forest area values detected")

        # Validate area arithmetic
        diff = (df["forest_area_ha"] + df["non_forest_area_ha"]) - df["total_lease_area_ha"]
        if (diff.abs() > 0.05).any():
            errors.append("Forest + Non-forest area does not equal total_lease_area_ha (variance > 0.05 Ha)")

        if "provenance_category" in df.columns:
            invalid_prov = df[~df["provenance_category"].isin(VALID_PROVENANCE_CATEGORIES)]["provenance_category"].tolist()
            if invalid_prov:
                errors.append(f"Invalid provenance_category values: {invalid_prov}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_dsr_boundary_pillars(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        required_cols = [
            "mine_id", "pillar_id", "pillar_sequence", "latitude", "longitude",
            "utm_easting", "utm_northing", "data_status", "provenance_status"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            errors.append(f"Missing required columns in boundary pillars: {missing}")
            return False, errors

        if df.duplicated(subset=["mine_id", "pillar_id"]).any():
            errors.append("Duplicate (mine_id, pillar_id) pairs detected in boundary pillars")
        if not df["latitude"].between(20.0, 24.0).all():
            errors.append("Pillar latitudes outside valid Central India range [20.0, 24.0]")
        if not df["longitude"].between(78.0, 82.0).all():
            errors.append("Pillar longitudes outside valid Central India range [78.0, 82.0]")
        if not df["utm_easting"].between(100000.0, 900000.0).all():
            errors.append("Pillar UTM Easting outside valid UTM Zone 44N range")
        if not df["utm_northing"].between(2000000.0, 3000000.0).all():
            errors.append("Pillar UTM Northing outside valid UTM Zone 44N range")

        if "provenance_category" in df.columns:
            invalid_prov = df[~df["provenance_category"].isin(VALID_PROVENANCE_CATEGORIES)]["provenance_category"].tolist()
            if invalid_prov:
                errors.append(f"Invalid provenance_category values: {invalid_prov}")

        if "point_type" in df.columns:
            invalid_pts = df[~df["point_type"].isin(VALID_POINT_TYPES)]["point_type"].tolist()
            if invalid_pts:
                errors.append(f"Invalid point_type values: {invalid_pts}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_dsr_boundaries_geojson(geojson_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        if geojson_dict.get("type") != "FeatureCollection":
            errors.append("GeoJSON root type must be 'FeatureCollection'")
            return False, errors

        features = geojson_dict.get("features", [])
        if not features:
            errors.append("GeoJSON contains zero features")
            return False, errors

        for idx, feat in enumerate(features):
            geom = feat.get("geometry", {})
            g_type = geom.get("type")
            coords = geom.get("coordinates", [])
            props = feat.get("properties", {})

            if g_type == "Polygon":
                if not coords or len(coords[0]) < 4:
                    errors.append(f"Feature {idx}: Polygon must have at least 4 coordinate tuples")
                elif coords[0][0] != coords[0][-1]:
                    errors.append(f"Feature {idx}: Polygon is unclosed (first coordinate != last coordinate)")
                else:
                    # Check for duplicate consecutive vertices (excluding final closure)
                    ring = coords[0][:-1]
                    for i in range(len(ring)):
                        if ring[i] == ring[(i + 1) % len(ring)]:
                            errors.append(f"Feature {idx}: Polygon contains duplicate consecutive vertices at index {i}")

                    # Check projected area calculation
                    try:
                        calc_area = DataValidator.calculate_projected_polygon_area_ha(coords[0])
                        if calc_area <= 0:
                            errors.append(f"Feature {idx}: Calculated projected polygon area is non-positive ({calc_area})")
                    except Exception as e:
                        errors.append(f"Feature {idx}: Projected area calculation error: {str(e)}")

            elif g_type == "Point":
                if not coords or len(coords) != 2:
                    errors.append(f"Feature {idx}: Point must have exactly 2 coordinates [lon, lat]")
                else:
                    lon, lat = coords
                    if not (78.0 <= lon <= 82.0) or not (20.0 <= lat <= 24.0):
                        errors.append(f"Feature {idx}: Point coordinates [{lon}, {lat}] outside Central India bounds")
            else:
                errors.append(f"Feature {idx}: Unsupported geometry type '{g_type}'")

            # Properties provenance validation
            if "provenance_category" in props:
                prov = props["provenance_category"]
                if prov not in VALID_PROVENANCE_CATEGORIES:
                    errors.append(f"Feature {idx}: Invalid provenance_category '{prov}'")

            if "point_type" in props:
                pt = props["point_type"]
                if pt not in VALID_POINT_TYPES:
                    errors.append(f"Feature {idx}: Invalid point_type '{pt}'")

        return len(errors) == 0, errors

    @staticmethod
    def validate_dsr_geology_reference(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        required_cols = [
            "formation_id", "group_name", "formation_name", "stratigraphic_order",
            "lithology_description", "manganese_ore_association", "source_name"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            errors.append(f"Missing required columns in geology reference: {missing}")
            return False, errors

        if df["formation_id"].duplicated().any():
            errors.append("Duplicate formation_ids detected in geology reference")
        if (df["stratigraphic_order"] <= 0).any():
            errors.append("Invalid non-positive stratigraphic_order detected")

        return len(errors) == 0, errors

    @staticmethod
    def validate_dsr_grade_reference(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        required_cols = [
            "grade_id", "mine_id", "grade_category", "mn_typical_pct",
            "fe_typical_pct", "sio2_typical_pct", "p_typical_pct", "source_name"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            errors.append(f"Missing required columns in grade reference: {missing}")
            return False, errors

        if (df["mn_typical_pct"] < 0).any() or (df["mn_typical_pct"] > 100).any():
            errors.append("mn_typical_pct outside [0, 100]")
        if (df["p_typical_pct"] < 0).any() or (df["p_typical_pct"] > 10).any():
            errors.append("p_typical_pct outside realistic range [0, 10]")

        return len(errors) == 0, errors

    @staticmethod
    def validate_dsr_production_reference(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        required_cols = [
            "record_id", "financial_year", "reporting_level", "mine_id",
            "production_tonnes", "production_status", "data_status"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            errors.append(f"Missing required columns in production reference: {missing}")
            return False, errors

        valid_statuses = {"reported_actual", "reported_aggregate", "planned", "simulated"}
        invalid = df[~df["production_status"].isin(valid_statuses)]["production_status"].tolist()
        if invalid:
            errors.append(f"Invalid production_status values: {invalid}")

        if (df["production_tonnes"] < 0).any():
            errors.append("Negative production_tonnes detected")

        return len(errors) == 0, errors

    @staticmethod
    def validate_dsr_constraints(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        required_cols = [
            "constraint_id", "mine_id", "constraint_category", "constraint_name",
            "value", "unit", "constraint_status", "source_name"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            errors.append(f"Missing required columns in constraints: {missing}")
            return False, errors

        valid_statuses = {"reported", "planned", "historical", "requires_current_validation"}
        invalid = df[~df["constraint_status"].isin(valid_statuses)]["constraint_status"].tolist()
        if invalid:
            errors.append(f"Invalid constraint_status values: {invalid}")

        return len(errors) == 0, errors
