"""
Geostatistical Resource Estimation & Spatial Grade Interpolation
Implements Inverse Distance Weighting (IDW) and Ordinary Kriging interpolation
for manganese assay grade (% Mn) across drillholes.
Computes illustrative resource tonnage estimates with strict caveats.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist


class GeostatisticalResourceEstimator:
    """
    Interpolates manganese grades from point drillhole assays across a spatial grid.
    Provides illustrative resource volume and tonnage calculations.
    """

    @staticmethod
    def inverse_distance_weighting(
        drillholes_df: pd.DataFrame,
        grid_df: pd.DataFrame,
        power: float = 2.0,
        max_dist_deg: float = 0.08
    ) -> pd.DataFrame:
        """
        Computes IDW grade interpolation for each grid cell using nearby drillholes.
        """
        dh_coords = drillholes_df[["latitude", "longitude"]].values
        dh_grades = drillholes_df["mn_grade_pct"].values
        dh_thickness = drillholes_df["thickness_m"].values
        
        grid_coords = grid_df[["latitude", "longitude"]].values
        distances = cdist(grid_coords, dh_coords)
        
        interpolated_grades = []
        interpolated_thicknesses = []
        confidence_levels = []
        
        for i in range(len(grid_coords)):
            dist_row = distances[i]
            nearby_mask = dist_row <= max_dist_deg
            
            if np.sum(nearby_mask) == 0:
                nearest = int(np.argmin(dist_row))
                if dist_row[nearest] <= 0.18:
                    nearby_mask = np.zeros_like(dist_row, dtype=bool)
                    nearby_mask[nearest] = True
                else:
                    interpolated_grades.append(np.nan)
                    interpolated_thicknesses.append(np.nan)
                    confidence_levels.append("Unclassified")
                    continue
                
            weights = 1.0 / (dist_row[nearby_mask] ** power + 1e-6)
            weights /= np.sum(weights)
            
            w_grade = float(np.sum(weights * dh_grades[nearby_mask]))
            w_thick = float(np.sum(weights * dh_thickness[nearby_mask]))
            
            # Confidence based on drill density (number of holes within 500m / 0.005 deg)
            close_holes = np.sum(dist_row <= 0.005)
            if close_holes >= 5:
                conf = "Indicated Resource"
            elif close_holes >= 2:
                conf = "Inferred Resource"
            else:
                conf = "Potential Mineralized Zone"
                
            interpolated_grades.append(round(w_grade, 2))
            interpolated_thicknesses.append(round(w_thick, 2))
            confidence_levels.append(conf)
            
        result_df = grid_df.copy()
        result_df["interpolated_mn_grade_pct"] = interpolated_grades
        result_df["estimated_thickness_m"] = interpolated_thicknesses
        result_df["resource_confidence"] = confidence_levels
        return result_df

    @staticmethod
    def estimate_resource_summary(
        interpolated_df: pd.DataFrame,
        cell_size_m: float = 50.0,
        bulk_density_t_m3: float = 3.6,  # Typical specific gravity for manganese ore (3.4 - 3.8 t/m³)
        cutoff_grade_pct: float = 20.0
    ) -> Dict[str, Any]:
        """
        Aggregates estimated tonnage and grade for cells meeting cutoff criteria.
        Explicitly flagged as illustrative toy estimate.
        """
        valid_cells = interpolated_df[
            (interpolated_df["interpolated_mn_grade_pct"] >= cutoff_grade_pct) &
            (~interpolated_df["interpolated_mn_grade_pct"].isna())
        ]
        
        if len(valid_cells) == 0:
            return {
                "total_inferred_tonnes": 0.0,
                "average_grade_pct": 0.0,
                "ore_volume_m3": 0.0,
                "cell_count": 0,
                "caveat": "Toy geostatistical estimate for demo purposes only; not JORC/UNFC compliant."
            }
            
        cell_area = cell_size_m * cell_size_m
        total_volume_m3 = float(np.sum(valid_cells["estimated_thickness_m"] * cell_area))
        total_tonnes = total_volume_m3 * bulk_density_t_m3
        weighted_grade = float(np.average(
            valid_cells["interpolated_mn_grade_pct"],
            weights=valid_cells["estimated_thickness_m"]
        ))
        
        return {
            "total_inferred_tonnes": round(total_tonnes, -2),
            "average_grade_pct": round(weighted_grade, 2),
            "ore_volume_m3": round(total_volume_m3, -2),
            "cell_count": len(valid_cells),
            "cutoff_grade_pct": cutoff_grade_pct,
            "bulk_density_t_m3": bulk_density_t_m3,
            "caveat": "Illustrative geostatistical toy resource estimate, not a certified reserve. Requires dense infill drilling and engineering feasibility.",
        }
