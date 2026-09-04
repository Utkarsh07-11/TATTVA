"""
Shortfall Prediction & Risk Assessment Engine for SIH 2026 PS 26009
Computes derived shortfall probability P(Forecast < Target) from quantile spread,
expected deficit tonnes, and risk categorization.
"""

from typing import Dict, Any, Tuple
import math
import numpy as np


class ShortfallRiskEstimator:
    """Computes shortfall risk metrics and categorical ratings."""

    @staticmethod
    def evaluate_shortfall(
        forecast_tonnes: float,
        interval_90: Tuple[float, float],
        target_tonnes: float,
        mine_block_id: str = "BLOCK_A",
        horizon_days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculates P(Production < Target) using quantile-spread uncertainty model:
        sigma_approx = (q90 - q10) / 2.563
        z = (target - forecast) / sigma_approx
        P(Shortfall) = Phi(z)
        """
        p10, p90 = interval_90
        expected_shortfall = max(0.0, round(target_tonnes - forecast_tonnes, 1))
        
        # Approximate standard deviation from 90% prediction interval
        spread = max(1.0, p90 - p10)
        sigma = spread / 2.5631
        
        # Standard normal CDF: 0.5 * (1 + erf(z / sqrt(2)))
        z = (target_tonnes - forecast_tonnes) / sigma
        shortfall_prob = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
        shortfall_prob = float(np.clip(shortfall_prob, 0.01, 0.99))
        shortfall_prob = round(shortfall_prob, 2)
        
        # Categorical risk level
        if shortfall_prob >= 0.85:
            risk_level = "CRITICAL"
        elif shortfall_prob >= 0.60:
            risk_level = "HIGH"
        elif shortfall_prob >= 0.30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            
        shortfall_pct = round((expected_shortfall / target_tonnes) * 100, 1) if target_tonnes > 0 else 0.0
        
        return {
            "mine_block_id": mine_block_id,
            "target_tonnes": target_tonnes,
            "forecast_tonnes": forecast_tonnes,
            "forecast_interval_90": [p10, p90],
            "expected_shortfall_tonnes": expected_shortfall,
            "shortfall_pct": shortfall_pct,
            "shortfall_probability": shortfall_prob,
            "risk_level": risk_level,
            "horizon_days": horizon_days,
        }
