"""
Reusable Real Geospatial Raster Feature Extractor
Extracts point and regular grid samples from authoritative GeoTIFF rasters (Sentinel-2, DEM).
Supports coordinate transformations (WGS84 <-> UTM), bounds checking, nodata handling,
and windowed/streaming batch access without loading full rasters into RAM.
"""

from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional, Union
import numpy as np
import pandas as pd
import rasterio
from rasterio.crs import CRS
from rasterio.windows import from_bounds
from pyproj import Transformer


class RasterExtractor:
    """
    Single-raster extractor for sampling values at point or batch coordinates.
    Handles coordinate transformations, bounds checking, and nodata masking.
    """

    def __init__(self, raster_path: Union[str, Path], feature_name: Optional[str] = None):
        self.raster_path = Path(raster_path)
        if not self.raster_path.exists():
            raise FileNotFoundError(f"Raster file not found: {self.raster_path}")

        self.feature_name = feature_name or self.raster_path.stem
        self._inspect_metadata()

    def _inspect_metadata(self) -> None:
        """Inspects raster headers without loading data array into RAM."""
        with rasterio.open(self.raster_path) as src:
            self.crs = src.crs
            self.crs_string = src.crs.to_string() if src.crs else "EPSG:4326"
            self.transform = src.transform
            self.bounds = src.bounds
            self.res = src.res
            self.shape = src.shape
            self.nodata = src.nodata
            self.dtypes = src.dtypes
            self.count = src.count

    def get_metadata(self) -> Dict[str, Any]:
        """Returns metadata dictionary for provenance reporting."""
        return {
            "feature_name": self.feature_name,
            "raster_path": str(self.raster_path),
            "crs": self.crs_string,
            "resolution": list(self.res),
            "shape": list(self.shape),
            "bounds": {
                "left": self.bounds.left,
                "bottom": self.bounds.bottom,
                "right": self.bounds.right,
                "top": self.bounds.top,
            },
            "nodata": self.nodata,
            "count": self.count,
        }

    def _transform_coords(
        self, coords: List[Tuple[float, float]], input_crs: str
    ) -> List[Tuple[float, float]]:
        """Transforms coordinates from input_crs to the raster's native CRS."""
        in_crs_obj = CRS.from_user_input(input_crs)
        if in_crs_obj == self.crs:
            return coords

        transformer = Transformer.from_crs(in_crs_obj, self.crs, always_xy=True)
        xs, ys = zip(*coords)
        trans_xs, trans_ys = transformer.transform(xs, ys)
        return list(zip(trans_xs, trans_ys))

    def sample_point(
        self, x: float, y: float, input_crs: Optional[str] = None
    ) -> Tuple[Optional[float], bool]:
        """
        Samples the raster at a single point (x, y).
        Returns:
            (value, is_valid)
        """
        vals, valids = self.sample_batch([(x, y)], input_crs=input_crs)
        return vals[0], bool(valids[0])

    def sample_batch(
        self,
        coords: List[Tuple[float, float]],
        input_crs: Optional[str] = None,
        band_idx: int = 1,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Samples raster at a list of (x, y) coordinates.
        Args:
            coords: List of (x, y) or (lon, lat) tuples.
            input_crs: CRS of input coords (e.g. 'EPSG:4326', 'EPSG:32644'). Defaults to raster CRS.
            band_idx: 1-indexed band number (default 1).
        Returns:
            values: 1D numpy array of sampled values (float64, np.nan for invalid/out-of-bounds/nodata).
            is_valid: 1D boolean numpy array indicating valid observations.
        """
        if not coords:
            return np.array([], dtype=np.float64), np.array([], dtype=bool)

        if input_crs is not None:
            trans_coords = self._transform_coords(coords, input_crs)
        else:
            trans_coords = coords

        n_points = len(trans_coords)
        values = np.full(n_points, np.nan, dtype=np.float64)
        is_valid = np.zeros(n_points, dtype=bool)

        # Separate inside bounds vs outside bounds
        b_left, b_bottom, b_right, b_top = self.bounds.left, self.bounds.bottom, self.bounds.right, self.bounds.top
        
        in_bounds_indices = []
        in_bounds_coords = []

        for idx, (px, py) in enumerate(trans_coords):
            if b_left <= px <= b_right and b_bottom <= py <= b_top:
                in_bounds_indices.append(idx)
                in_bounds_coords.append((px, py))

        if in_bounds_coords:
            with rasterio.open(self.raster_path) as src:
                # rasterio.sample takes [(x, y), ...] in raster native CRS
                raw_samples = list(src.sample(in_bounds_coords, indexes=band_idx))
                
                for idx_orig, raw_val in zip(in_bounds_indices, raw_samples):
                    v = float(raw_val[0])
                    # Check nodata and NaN
                    if self.nodata is not None and (v == self.nodata or np.isclose(v, self.nodata, atol=1e-4)):
                        continue
                    if np.isnan(v):
                        continue
                    values[idx_orig] = v
                    is_valid[idx_orig] = True

        return values, is_valid


class MultiRasterExtractor:
    """
    Multi-raster feature extractor that manages multiple raster datasets (Sentinel-2 bands,
    derived spectral indices, DEM terrain attributes) and samples them simultaneously onto
    an analysis coordinate grid or point collection.
    """

    def __init__(self):
        self.extractors: Dict[str, RasterExtractor] = {}

    def register_raster(
        self, feature_name: str, raster_path: Union[str, Path]
    ) -> RasterExtractor:
        """Registers a raster dataset under an explicit feature name."""
        extractor = RasterExtractor(raster_path, feature_name=feature_name)
        self.extractors[feature_name] = extractor
        return extractor

    def get_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Returns metadata for all registered raster datasets."""
        return {name: ext.get_metadata() for name, ext in self.extractors.items()}

    def extract_features(
        self,
        coords: List[Tuple[float, float]],
        input_crs: str = "EPSG:32644",
        include_quality: bool = True,
    ) -> pd.DataFrame:
        """
        Extracts all registered raster features at given coordinates.
        Args:
            coords: List of (x, y) or (lon, lat) tuples.
            input_crs: CRS of coords.
            include_quality: Whether to compute valid_feature_fraction and feature_quality.
        Returns:
            pd.DataFrame with feature columns and quality metrics.
        """
        df_dict = {}
        valid_masks = {}

        for feature_name, extractor in self.extractors.items():
            vals, valids = extractor.sample_batch(coords, input_crs=input_crs)
            df_dict[feature_name] = vals
            valid_masks[feature_name] = valids

        df = pd.DataFrame(df_dict)

        if include_quality and self.extractors:
            valid_matrix = np.column_stack(list(valid_masks.values()))
            valid_counts = np.sum(valid_matrix, axis=1)
            total_features = len(self.extractors)
            valid_fraction = valid_counts / float(total_features)

            df["valid_feature_fraction"] = np.round(valid_fraction, 4)

            # Categorize feature_quality
            quality = np.full(len(coords), "invalid", dtype=object)
            quality[valid_fraction == 1.0] = "valid"
            quality[(valid_fraction > 0.0) & (valid_fraction < 1.0)] = "partial"
            df["feature_quality"] = quality

        return df

    @staticmethod
    def generate_regular_grid(
        bounds: Tuple[float, float, float, float],
        spacing_m: float = 30.0,
        crs: str = "EPSG:32644",
        id_prefix: str = "GRID",
    ) -> pd.DataFrame:
        """
        Generates regular point sampling grid covering the given bounds at spacing_m.
        Args:
            bounds: (min_x, min_y, max_x, max_y) in meters (projected CRS).
            spacing_m: Grid spacing in meters (e.g. 30.0).
            crs: Projected coordinate system (default 'EPSG:32644').
            id_prefix: Prefix for cell_id.
        Returns:
            pd.DataFrame with columns ['cell_id', 'x', 'y', 'longitude', 'latitude'].
        """
        min_x, min_y, max_x, max_y = bounds
        half_res = spacing_m / 2.0

        # Generate center coordinates
        xs = np.arange(min_x + half_res, max_x, spacing_m)
        ys = np.arange(max_y - half_res, min_y, -spacing_m)

        grid_x, grid_y = np.meshgrid(xs, ys)
        flat_x = grid_x.ravel()
        flat_y = grid_y.ravel()

        # Transform to WGS84 Longitude / Latitude
        trans_to_wgs84 = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
        lons, lats = trans_to_wgs84.transform(flat_x, flat_y)

        n_cells = len(flat_x)
        cell_ids = [f"{id_prefix}-{i+1:05d}" for i in range(n_cells)]

        grid_df = pd.DataFrame({
            "cell_id": cell_ids,
            "x": np.round(flat_x, 2),
            "y": np.round(flat_y, 2),
            "longitude": np.round(lons, 6),
            "latitude": np.round(lats, 6),
        })

        return grid_df
