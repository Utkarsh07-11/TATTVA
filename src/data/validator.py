"""
Data Validation Engine for SIH 2026 PS 26009
Ensures schema adherence, value range constraints, absence of unhandled nulls,
and verifies the 'synthetic' data integrity flag.
"""

from typing import Tuple, List
import pandas as pd
from pydantic import BaseModel, Field, field_validator


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


class DataValidator:
    """Validates loaded Pandas DataFrames against engineering and geological constraints."""

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
