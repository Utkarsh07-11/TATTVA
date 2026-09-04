"""
Manganese Prospectivity Model for SIH 2026 PS 26009
XGBoost-based spatial classifier estimating probability of manganese mineralization.
Trained with Spatial Block Cross-Validation to eliminate spatial autocorrelation leakage.
Converts predictions into a standardized GeoJSON probability surface.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, average_precision_score

from config.settings import settings
from src.features.spatial import SpatialFeatureEngineer

class ProspectivityModel:
    def __init__(self):
        self.feature_cols = [
            "elevation_m", "slope_deg", "aspect_deg", "ndvi", "ndwi",
            "iron_oxide_index", "clay_index", "ferrous_index", "lst_k"
        ]
        self.model = XGBClassifier(
            n_estimators=120,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="logloss"
        )
        self.is_trained = False
        self.spatial_cv_metrics: Dict[str, float] = {}

    def train_with_spatial_cv(
        self,
        drillholes_df: pd.DataFrame,
        satellite_grid_df: pd.DataFrame,
        n_blocks: int = 4
    ) -> Dict[str, float]:
        """
        Trains the prospectivity model using Spatial Block Cross-Validation.
        Returns mean cross-validation evaluation metrics.
        """
        fused_df = SpatialFeatureEngineer.sample_satellite_at_drillholes(drillholes_df, satellite_grid_df)
        
        cv_scores = {"precision": [], "recall": [], "f1": [], "roc_auc": [], "pr_auc": []}
        
        for train_df, val_df in SpatialFeatureEngineer.spatial_block_splits(fused_df, n_blocks=n_blocks):
            X_tr = train_df[self.feature_cols]
            y_tr = train_df["is_ore_bearing"]
            X_val = val_df[self.feature_cols]
            y_val = val_df["is_ore_bearing"]
            
            fold_model = XGBClassifier(
                n_estimators=100, max_depth=4, learning_rate=0.08,
                random_state=42, eval_metric="logloss"
            )
            fold_model.fit(X_tr, y_tr)
            
            val_probs = fold_model.predict_proba(X_val)[:, 1]
            val_preds = (val_probs >= 0.5).astype(int)
            
            cv_scores["precision"].append(precision_score(y_val, val_preds, zero_division=0))
            cv_scores["recall"].append(recall_score(y_val, val_preds, zero_division=0))
            cv_scores["f1"].append(f1_score(y_val, val_preds, zero_division=0))
            cv_scores["roc_auc"].append(roc_auc_score(y_val, val_probs) if len(np.unique(y_val)) > 1 else 0.5)
            cv_scores["pr_auc"].append(average_precision_score(y_val, val_probs) if len(np.unique(y_val)) > 1 else 0.5)
            
        self.spatial_cv_metrics = {k: float(np.mean(v)) for k, v in cv_scores.items()}
        
        # Fit final model on all data
        X_all = fused_df[self.feature_cols]
        y_all = fused_df["is_ore_bearing"]
        self.model.fit(X_all, y_all)
        self.is_trained = True
        
        return self.spatial_cv_metrics

    def predict_grid_surface(self, satellite_grid_df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes prospectivity probability per cell across the entire satellite grid.
        """
        if not self.is_trained:
            raise RuntimeError("Prospectivity model is not trained yet.")
            
        X_grid = satellite_grid_df[self.feature_cols]
        probs = self.model.predict_proba(X_grid)[:, 1]
        
        result_df = satellite_grid_df.copy()
        result_df["prospectivity_prob"] = np.round(probs, 4)
        
        # Uncertainty approximation via logistic margin: 1 - 2*|prob - 0.5|
        result_df["uncertainty"] = np.round(1.0 - 2.0 * np.abs(probs - 0.5), 4)
        
        # Prospectivity Category
        conditions = [
            result_df["prospectivity_prob"] >= 0.70,
            (result_df["prospectivity_prob"] >= 0.45) & (result_df["prospectivity_prob"] < 0.70),
            result_df["prospectivity_prob"] < 0.45,
        ]
        choices = ["High Potential", "Moderate Potential", "Low Potential / Barren"]
        result_df["prospectivity_class"] = np.select(conditions, choices, default="Unclassified")
        
        return result_df

    def to_geojson_feature_collection(self, scored_grid_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Converts scored grid cells into a GeoJSON FeatureCollection of polygonal grid bounding boxes
        suitable for direct Leaflet/Mapbox rendering.
        """
        # Cell half-width in degrees (~30m-50m cell)
        lat_step = 0.00114 / 2.0
        lon_step = 0.00114 / 2.0
        
        features = []
        for _, row in scored_grid_df.iterrows():
            lat = row["latitude"]
            lon = row["longitude"]
            
            coords = [[
                [lon - lon_step, lat - lat_step],
                [lon + lon_step, lat - lat_step],
                [lon + lon_step, lat + lat_step],
                [lon - lon_step, lat + lat_step],
                [lon - lon_step, lat - lat_step],
            ]]
            
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": coords
                },
                "properties": {
                    "grid_id": row["grid_id"],
                    "latitude": lat,
                    "longitude": lon,
                    "prospectivity_prob": float(row["prospectivity_prob"]),
                    "uncertainty": float(row["uncertainty"]),
                    "prospectivity_class": row["prospectivity_class"],
                    "iron_oxide_index": float(row.get("iron_oxide_index", 0.0)),
                    "clay_index": float(row.get("clay_index", 0.0)),
                    "elevation_m": float(row.get("elevation_m", 0.0)),
                    "slope_deg": float(row.get("slope_deg", 0.0)),
                }
            })
            
        return {
            "type": "FeatureCollection",
            "metadata": {
                "description": "Manganese Prospectivity Probability Surface",
                "spatial_cv_metrics": self.spatial_cv_metrics,
                "caveat": "Data-driven likelihood of manganese occurrence, not a certified reserve.",
            },
            "features": features
        }

    def save(self, model_path: Path):
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "feature_cols": self.feature_cols,
            "spatial_cv_metrics": self.spatial_cv_metrics,
            "is_trained": self.is_trained
        }, model_path)

    @classmethod
    def load(cls, model_path: Path) -> "ProspectivityModel":
        data = joblib.load(model_path)
        inst = cls()
        inst.model = data["model"]
        inst.feature_cols = data["feature_cols"]
        inst.spatial_cv_metrics = data["spatial_cv_metrics"]
        inst.is_trained = data["is_trained"]
        return inst
