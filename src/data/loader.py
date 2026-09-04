"""
Data Loading & Caching Engine for SIH 2026 PS 26009
Loads and parses CSVs and GeoJSONs from data directories, running validation checks.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

from config.settings import settings
from src.data.validator import DataValidator

class DataLoader:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or settings.PROCESSED_DATA_DIR
        self._production_df: Optional[pd.DataFrame] = None
        self._equipment_df: Optional[pd.DataFrame] = None
        self._drillhole_df: Optional[pd.DataFrame] = None
        self._satellite_df: Optional[pd.DataFrame] = None
        self._mine_blocks_geojson: Optional[Dict[str, Any]] = None

    def load_production_data(self, force_reload: bool = False) -> pd.DataFrame:
        if self._production_df is None or force_reload:
            file_path = self.data_dir / "production_daily.csv"
            if not file_path.exists():
                file_path = settings.SYNTHETIC_DATA_DIR / "production_daily.csv"
            df = pd.read_csv(file_path)
            df["date"] = pd.to_datetime(df["date"])
            valid, errors = DataValidator.validate_production(df)
            if not valid:
                raise ValueError(f"Production data validation failed: {errors}")
            self._production_df = df
        return self._production_df.copy()

    def load_equipment_events(self, force_reload: bool = False) -> pd.DataFrame:
        if self._equipment_df is None or force_reload:
            file_path = self.data_dir / "equipment_events.csv"
            if not file_path.exists():
                file_path = settings.SYNTHETIC_DATA_DIR / "equipment_events.csv"
            df = pd.read_csv(file_path)
            df["start_time"] = pd.to_datetime(df["start_time"])
            df["end_time"] = pd.to_datetime(df["end_time"])
            self._equipment_df = df
        return self._equipment_df.copy()

    def load_drillhole_assay(self, force_reload: bool = False) -> pd.DataFrame:
        if self._drillhole_df is None or force_reload:
            file_path = self.data_dir / "drillhole_assay.csv"
            if not file_path.exists():
                file_path = settings.SYNTHETIC_DATA_DIR / "drillhole_assay.csv"
            df = pd.read_csv(file_path)
            valid, errors = DataValidator.validate_drillholes(df)
            if not valid:
                raise ValueError(f"Drillhole data validation failed: {errors}")
            self._drillhole_df = df
        return self._drillhole_df.copy()

    def load_satellite_grid(self, force_reload: bool = False) -> pd.DataFrame:
        if self._satellite_df is None or force_reload:
            file_path = self.data_dir / "satellite_features_grid.csv"
            if not file_path.exists():
                file_path = settings.SYNTHETIC_DATA_DIR / "satellite_features_grid.csv"
            df = pd.read_csv(file_path)
            valid, errors = DataValidator.validate_satellite_grid(df)
            if not valid:
                raise ValueError(f"Satellite grid data validation failed: {errors}")
            self._satellite_df = df
        return self._satellite_df.copy()

    def load_mine_blocks_geojson(self, force_reload: bool = False) -> Dict[str, Any]:
        if self._mine_blocks_geojson is None or force_reload:
            file_path = self.data_dir / "mine_blocks.geojson"
            if not file_path.exists():
                file_path = settings.SYNTHETIC_DATA_DIR / "mine_blocks.geojson"
            with open(file_path, "r") as f:
                self._mine_blocks_geojson = json.load(f)
        return self._mine_blocks_geojson

# Global singleton loader instance
data_loader = DataLoader()
