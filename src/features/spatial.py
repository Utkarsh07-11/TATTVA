"""
Spatial Feature Engineering & Spatial Block Cross-Validation
Implements spatial clustering to avoid spatial autocorrelation leakage in prospectivity modeling.
Integrates drillhole assay points with satellite proxies (Sentinel-2 band ratios, DEM slope/aspect).
"""

from typing import Tuple, List, Generator
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from scipy.spatial import cKDTree


class SpatialFeatureEngineer:
    """Fuses point assay observations with geospatial satellite and terrain grids."""

    @staticmethod
    def sample_satellite_at_drillholes(
        drillholes_df: pd.DataFrame,
        satellite_grid_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Performs nearest-neighbor spatial join from satellite grid to drillhole collar locations.
        """
        grid_coords = satellite_grid_df[["latitude", "longitude"]].values
        dh_coords = drillholes_df[["latitude", "longitude"]].values
        
        tree = cKDTree(grid_coords)
        distances, indices = tree.query(dh_coords)
        
        matched_sat = satellite_grid_df.iloc[indices].reset_index(drop=True)
        
        # Merge satellite columns into drillholes
        feature_cols = [
            "elevation_m", "slope_deg", "aspect_deg", "ndvi", "ndwi",
            "iron_oxide_index", "clay_index", "ferrous_index", "lst_k"
        ]
        
        merged_df = drillholes_df.copy().reset_index(drop=True)
        for col in feature_cols:
            merged_df[col] = matched_sat[col]
            
        merged_df["dist_to_grid_center_deg"] = distances
        return merged_df

    @staticmethod
    def spatial_block_splits(
        df: pd.DataFrame,
        n_blocks: int = 4,
        random_state: int = 42
    ) -> Generator[Tuple[pd.DataFrame, pd.DataFrame], None, None]:
        """
        Performs Spatial Block Cross-Validation using K-Means clustering on coordinates.
        Ensures entire geographic sectors are held out to test true spatial generalization
        rather than memorizing nearby drillhole assays.
        """
        coords = df[["latitude", "longitude"]].values
        kmeans = KMeans(n_clusters=n_blocks, random_state=random_state, n_init=10)
        df["spatial_block"] = kmeans.fit_predict(coords)
        
        for block_id in range(n_blocks):
            train_mask = df["spatial_block"] != block_id
            test_mask = df["spatial_block"] == block_id
            
            yield df[train_mask].copy(), df[test_mask].copy()
