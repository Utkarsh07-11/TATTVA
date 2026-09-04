"""
End-to-End Training & Cross-Validation Pipeline for SIH 2026 PS 26009
Trains both:
1. Geospatial Prospectivity Model (XGBoost + Spatial Block CV)
2. Production Forecasting Engine (LightGBM Quantile Regression + Rolling-Origin CV)
Saves serialized models, cross-validation metrics, and precomputed GeoJSON surfaces.
"""

import json
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import settings
from src.data.loader import data_loader
from src.models.prospectivity import ProspectivityModel
from src.models.forecasting import ProductionForecaster
from src.geospatial.kriging import GeostatisticalResourceEstimator


def run_pipeline():
    print("==========================================================")
    print("SIH 2026 PS 26009: Starting AI/ML Training Pipeline")
    print("==========================================================")
    
    # 1. Load Datasets
    print("\n[Step 1/4] Ingesting & Validating Multi-Source Data...")
    prod_df = data_loader.load_production_data()
    dh_df = data_loader.load_drillhole_assay()
    sat_df = data_loader.load_satellite_grid()
    blocks_geo = data_loader.load_mine_blocks_geojson()
    print(f" Loaded {len(prod_df)} production records, {len(dh_df)} drillhole assays, {len(sat_df)} satellite grid cells.")
    
    # 2. Train Geospatial Prospectivity Model (Spatial Block CV)
    print("\n[Step 2/4] Training Manganese Prospectivity Model (Spatial Block CV)...")
    prospectivity_model = ProspectivityModel()
    spatial_metrics = prospectivity_model.train_with_spatial_cv(dh_df, sat_df, n_blocks=4)
    print(" Spatial Block Cross-Validation Results:")
    for metric, score in spatial_metrics.items():
        print(f"   -> {metric.upper()}: {score:.4f}")
        
    # Generate probability surface & save GeoJSON
    scored_grid_df = prospectivity_model.predict_grid_surface(sat_df)
    prospectivity_geojson = prospectivity_model.to_geojson_feature_collection(scored_grid_df)
    
    prospectivity_path = settings.MODELS_DIR / "prospectivity_model.pkl"
    prospectivity_model.save(prospectivity_path)
    
    surface_path = settings.PROCESSED_DATA_DIR / "prospectivity_surface.geojson"
    with open(surface_path, "w") as f:
        json.dump(prospectivity_geojson, f, indent=2)
    print(f" Saved prospectivity model to {prospectivity_path}")
    print(f" Exported GeoJSON probability surface to {surface_path}")
    
    # 3. Geostatistical Resource Estimation
    print("\n[Step 3/4] Computing Geostatistical Resource Grade Interpolation (IDW/Kriging)...")
    idw_df = GeostatisticalResourceEstimator.inverse_distance_weighting(dh_df, sat_df)
    resource_summary = GeostatisticalResourceEstimator.estimate_resource_summary(idw_df, cutoff_grade_pct=20.0)
    print(f" Toy Resource Estimate (Inferred): {resource_summary['total_inferred_tonnes']:,.0f} tonnes @ {resource_summary['average_grade_pct']}% Mn")
    
    resource_path = settings.PROCESSED_DATA_DIR / "resource_summary.json"
    with open(resource_path, "w") as f:
        json.dump(resource_summary, f, indent=2)
        
    # 4. Train Production Forecaster (Rolling-Origin CV)
    print("\n[Step 4/4] Training Production Forecaster (Rolling-Origin CV)...")
    forecaster = ProductionForecaster()
    cv_metrics = forecaster.train_with_rolling_cv(prod_df, n_splits=5, test_window_days=30)
    
    print(" Rolling-Origin Temporal Cross-Validation Results:")
    print(f"   -> LightGBM Quantile (P50) MAE: {cv_metrics['lightgbm_quantile']['mae']:.2f} t")
    print(f"   -> 90% Prediction Interval Coverage (PICP): {cv_metrics['lightgbm_quantile']['picp_coverage_90']*100:.1f}%")
    print(f"   -> Ridge Baseline MAE: {cv_metrics['ridge_baseline']['mae']:.2f} t")
    print(f"   -> Naive 7-Day Moving Avg MAE: {cv_metrics['naive_7d_baseline']['mae']:.2f} t")
    print(f"   -> ML Model Advantage over Naive: {cv_metrics['ml_advantage_pct']:.1f}% improvement")
    
    forecaster.save(settings.MODELS_DIR)
    print(f" Saved production forecaster models to {settings.MODELS_DIR}")
    
    # Save unified metrics summary
    metrics_summary = {
        "prospectivity_spatial_cv": spatial_metrics,
        "forecasting_rolling_cv": cv_metrics,
        "resource_estimation_summary": resource_summary,
        "status": "TRAINED_AND_VERIFIED",
    }
    with open(settings.MODELS_DIR / "metrics_summary.json", "w") as f:
        json.dump(metrics_summary, f, indent=2)
        
    print("\n==========================================================")
    print("Pipeline completed successfully! All models & surfaces cached.")
    print("==========================================================")


if __name__ == "__main__":
    run_pipeline()
