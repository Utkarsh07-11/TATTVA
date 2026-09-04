"""
Scenario Simulation Engine for SIH 2026 PS 26009
Re-scores the trained LightGBM production forecaster under actionable operational interventions
(fleet redeployment, blast rescheduling, maintenance acceleration).
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from src.models.forecasting import ProductionForecaster


class ScenarioSimulator:
    def __init__(self, forecaster: ProductionForecaster):
        self.forecaster = forecaster

    def simulate_action(
        self,
        base_features_df: pd.DataFrame,
        action_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        horizon_days: int = 30
    ) -> Dict[str, Any]:
        """
        Runs the forecaster under perturbed conditions corresponding to the candidate action.
        """
        parameters = parameters or {}
        overrides = {}
        
        if action_type == "redeploy_excavator":
            # Redeploying an excavator from a lower-priority block increases availability
            boost = parameters.get("availability_boost_pct", 18.0)
            base_avail = float(base_features_df["equipment_availability_pct"].iloc[-1])
            overrides["equipment_availability_pct"] = min(98.0, base_avail + boost)
            overrides["avail_roll_mean_7d"] = min(98.0, base_avail + boost * 0.7)
            
        elif action_type == "reschedule_blasting":
            # Rescheduling clears blasting delay flags and smooths blast counts
            overrides["blasting_delay_flag"] = 0
            overrides["blast_delay_count_7d"] = 0
            overrides["blast_delay_count_14d"] = 0
            
        elif action_type == "preventive_maintenance":
            # Completing PM clears maintenance downtime flag and improves mechanical availability
            overrides["maintenance_flag"] = 0
            base_avail = float(base_features_df["equipment_availability_pct"].iloc[-1])
            overrides["equipment_availability_pct"] = min(95.0, base_avail + 8.0)
            
        elif action_type == "custom_slider":
            # Direct parameters from frontend What-If sandbox sliders
            if "equipment_availability_pct" in parameters:
                overrides["equipment_availability_pct"] = float(parameters["equipment_availability_pct"])
            if "blasting_delay_flag" in parameters:
                overrides["blasting_delay_flag"] = int(parameters["blasting_delay_flag"])
            if "rainfall_mm" in parameters:
                overrides["rainfall_mm"] = float(parameters["rainfall_mm"])
                
        # 1. Baseline prediction
        baseline_res = self.forecaster.predict_horizon(base_features_df, horizon_days=horizon_days)
        base_tonnes = baseline_res["forecast_tonnes"]
        
        # 2. Perturbed prediction
        simulated_res = self.forecaster.predict_horizon(
            base_features_df,
            horizon_days=horizon_days,
            scenario_overrides=overrides
        )
        sim_tonnes = simulated_res["forecast_tonnes"]
        
        recovery_tonnes = max(0.0, round(sim_tonnes - base_tonnes, 1))
        
        return {
            "action_type": action_type,
            "baseline_tonnes": base_tonnes,
            "simulated_tonnes": sim_tonnes,
            "expected_recovery_tonnes": recovery_tonnes,
            "simulated_interval_90": simulated_res["interval_90"],
            "applied_overrides": overrides,
        }
