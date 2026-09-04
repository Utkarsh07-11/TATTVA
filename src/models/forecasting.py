"""
Production Forecasting Engine with LightGBM Quantile Regression
Implements probabilistic time-series forecasting (10th, 50th, 90th percentiles)
with exogenous operational regressors (equipment availability, weather, blasting).
Evaluated via forward-chaining rolling-origin cross validation against naive & ridge baselines.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error

from config.settings import settings
from src.features.temporal import TemporalFeatureEngineer

class ProductionForecaster:
    def __init__(self):
        self.feature_cols = [
            "equipment_availability_pct", "rainfall_mm", "blasting_delay_flag", "maintenance_flag",
            "tonnes_lag_1", "tonnes_lag_2", "tonnes_lag_7", "tonnes_lag_14", "tonnes_lag_30",
            "avail_lag_1", "avail_lag_2", "avail_lag_7",
            "prod_roll_mean_7d", "prod_roll_std_7d", "prod_roll_mean_14d", "prod_roll_std_14d",
            "avail_roll_mean_7d", "avail_roll_mean_14d",
            "rain_roll_sum_7d", "rain_roll_sum_14d",
            "blast_delay_count_7d", "blast_delay_count_14d",
            "day_of_week", "month", "is_monsoon"
        ]
        
        # Quantile regressors for uncertainty modeling
        self.models: Dict[float, LGBMRegressor] = {
            0.1: LGBMRegressor(objective="quantile", alpha=0.10, n_estimators=100, learning_rate=0.06, random_state=42, verbose=-1),
            0.5: LGBMRegressor(objective="quantile", alpha=0.50, n_estimators=120, learning_rate=0.06, random_state=42, verbose=-1),
            0.9: LGBMRegressor(objective="quantile", alpha=0.90, n_estimators=100, learning_rate=0.06, random_state=42, verbose=-1),
        }
        
        # Baselines
        self.ridge_baseline = Ridge(alpha=1.0)
        
        self.is_trained = False
        self.cv_metrics: Dict[str, Any] = {}

    def train_with_rolling_cv(
        self,
        production_df: pd.DataFrame,
        n_splits: int = 5,
        test_window_days: int = 30
    ) -> Dict[str, Any]:
        """
        Trains models using forward-chaining rolling-origin cross-validation.
        Prevents temporal leakage and benchmarks against Naive Moving Average and Ridge.
        """
        feat_df = TemporalFeatureEngineer.create_features(production_df)
        
        lgb_mae_list, ridge_mae_list, naive_mae_list = [], [], []
        coverage_list = []
        
        for train_slice, test_slice in TemporalFeatureEngineer.rolling_origin_splits(
            feat_df, n_splits=n_splits, test_window_days=test_window_days
        ):
            X_tr = train_slice[self.feature_cols]
            y_tr = train_slice["actual_tonnes"]
            X_te = test_slice[self.feature_cols]
            y_te = test_slice["actual_tonnes"]
            
            # 1. Fit Fold Quantile Models
            m10 = LGBMRegressor(objective="quantile", alpha=0.10, n_estimators=80, learning_rate=0.07, random_state=42, verbose=-1)
            m50 = LGBMRegressor(objective="quantile", alpha=0.50, n_estimators=80, learning_rate=0.07, random_state=42, verbose=-1)
            m90 = LGBMRegressor(objective="quantile", alpha=0.90, n_estimators=80, learning_rate=0.07, random_state=42, verbose=-1)
            
            m10.fit(X_tr, y_tr)
            m50.fit(X_tr, y_tr)
            m90.fit(X_tr, y_tr)
            
            preds_10 = m10.predict(X_te)
            preds_50 = m50.predict(X_te)
            preds_90 = m90.predict(X_te)
            
            lgb_mae = mean_absolute_error(y_te, preds_50)
            lgb_mae_list.append(lgb_mae)
            
            # Coverage: fraction of actuals inside [q10, q90]
            inside_interval = (y_te >= preds_10) & (y_te <= preds_90)
            coverage = np.mean(inside_interval)
            coverage_list.append(coverage)
            
            # 2. Ridge Baseline
            ridge = Ridge(alpha=1.0)
            ridge.fit(X_tr, y_tr)
            ridge_preds = ridge.predict(X_te)
            ridge_mae_list.append(mean_absolute_error(y_te, ridge_preds))
            
            # 3. Naive Baseline (7-day rolling mean lag)
            naive_preds = test_slice["prod_roll_mean_7d"]
            naive_mae_list.append(mean_absolute_error(y_te, naive_preds))
            
        self.cv_metrics = {
            "lightgbm_quantile": {
                "mae": float(np.mean(lgb_mae_list)),
                "picp_coverage_90": float(np.mean(coverage_list)),
            },
            "ridge_baseline": {
                "mae": float(np.mean(ridge_mae_list)),
            },
            "naive_7d_baseline": {
                "mae": float(np.mean(naive_mae_list)),
            },
            "ml_advantage_pct": float(np.round(((np.mean(naive_mae_list) - np.mean(lgb_mae_list)) / np.mean(naive_mae_list)) * 100, 2))
        }
        
        # Fit final models on full engineered dataset
        X_all = feat_df[self.feature_cols]
        y_all = feat_df["actual_tonnes"]
        
        for q, model in self.models.items():
            model.fit(X_all, y_all)
            
        self.ridge_baseline.fit(X_all, y_all)
        self.is_trained = True
        return self.cv_metrics

    def predict_horizon(
        self,
        recent_features_df: pd.DataFrame,
        horizon_days: int = 30,
        scenario_overrides: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Forecasts daily production and aggregates over the specified horizon.
        Optionally accepts scenario_overrides (e.g. availability +10%, blast delay = 0)
        to re-score the model for what-if simulation.
        """
        if not self.is_trained:
            raise RuntimeError("Forecasting models are not trained yet.")
            
        # Take the most recent feature record as base
        base_features = recent_features_df.iloc[-1:].copy()
        
        daily_forecasts_50 = []
        daily_forecasts_10 = []
        daily_forecasts_90 = []
        
        curr_feat = base_features.copy()
        
        # Apply scenario overrides if provided
        if scenario_overrides:
            for k, v in scenario_overrides.items():
                if k in curr_feat.columns:
                    curr_feat[k] = v
                    
        for day in range(horizon_days):
            X_input = curr_feat[self.feature_cols]
            
            p10 = max(0.0, float(self.models[0.1].predict(X_input)[0]))
            p50 = max(0.0, float(self.models[0.5].predict(X_input)[0]))
            p90 = max(p50, float(self.models[0.9].predict(X_input)[0]))
            
            daily_forecasts_10.append(round(p10, 1))
            daily_forecasts_50.append(round(p50, 1))
            daily_forecasts_90.append(round(p90, 1))
            
            # Simple autoregressive rollover for next step
            curr_feat["tonnes_lag_1"] = p50
            curr_feat["day_of_week"] = (curr_feat["day_of_week"] + 1) % 7
            
        total_forecast_50 = float(np.sum(daily_forecasts_50))
        total_forecast_10 = float(np.sum(daily_forecasts_10))
        total_forecast_90 = float(np.sum(daily_forecasts_90))
        
        return {
            "forecast_tonnes": round(total_forecast_50, 1),
            "interval_90": [round(total_forecast_10, 1), round(total_forecast_90, 1)],
            "daily_forecasts_50": daily_forecasts_50,
            "daily_forecasts_10": daily_forecasts_10,
            "daily_forecasts_90": daily_forecasts_90,
            "horizon_days": horizon_days,
        }

    def save(self, model_dir: Path):
        model_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "models": self.models,
            "ridge_baseline": self.ridge_baseline,
            "feature_cols": self.feature_cols,
            "cv_metrics": self.cv_metrics,
            "is_trained": self.is_trained,
        }, model_dir / "production_forecaster.pkl")

    @classmethod
    def load(cls, model_dir: Path) -> "ProductionForecaster":
        data = joblib.load(model_dir / "production_forecaster.pkl")
        inst = cls()
        inst.models = data["models"]
        inst.ridge_baseline = data["ridge_baseline"]
        inst.feature_cols = data["feature_cols"]
        inst.cv_metrics = data["cv_metrics"]
        inst.is_trained = data["is_trained"]
        return inst
