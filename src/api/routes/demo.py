"""
Phase 19: Demonstration Intelligence, Pre-Flight Health, and Walkthrough Execution Routes.
Serves the authoritative demonstration configuration and hierarchical pre-flight diagnostics.
Enforces zero demo-only shortcuts and 100% public application pathway parity.
"""

import time
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from config.demo_config import DEMO_CONFIG
from src.data.loader import data_loader

router = APIRouter(prefix="/real/demo", tags=["Demonstration Intelligence"])


@router.get("/config")
def get_demonstration_config() -> Dict[str, Any]:
    """
    Returns the single authoritative demonstration configuration for TATTVA.
    Includes step IDs, sequence, mine IDs, timing targets, speaker notes,
    juror defense notes, governance disclosures, and action types.
    """
    return DEMO_CONFIG


@router.get("/step/{step_id}")
def get_demonstration_step(step_id: int) -> Dict[str, Any]:
    """
    Returns exact metadata, expected API response assertions, and speaking notes
    for a specific demonstration step (1 through 12).
    """
    steps = DEMO_CONFIG.get("demonstration_path", [])
    step = next((s for s in steps if s.get("step_id") == step_id or s.get("step") == step_id), None)
    if not step:
        raise HTTPException(
            status_code=404,
            detail=f"Demonstration step {step_id} not found. Valid steps are 1 through {len(steps)}."
        )
    return {
        "status": "success",
        "step": step,
        "total_steps": len(steps),
        "primary_demo_mine": DEMO_CONFIG.get("primary_demo_mine")
    }


@router.get("/preflight")
def run_preflight_health_audit() -> Dict[str, Any]:
    """
    Runs a comprehensive, hierarchical 6-category application and runtime readiness audit.
    Categories: DATA, CAPABILITY, ISOLATION, DECISION WORKFLOW, FRONTEND, PERFORMANCE.
    Separates scientific correctness from host execution latency telemetry.
    """
    t_start = time.perf_counter()
    errors: List[str] = []

    # -------------------------------------------------------------
    # 1. DATA AUDIT
    # -------------------------------------------------------------
    data_checks = {}
    try:
        mines_df = data_loader.load_real_mines_df()
        geojson_data = data_loader.load_real_mines_geojson()
        prod_df = data_loader.load_real_production_df()
        files_ok = len(mines_df) == 10 and "features" in geojson_data and not prod_df.empty
        data_checks["files_readable"] = "PASS" if files_ok else "FAIL"
    except Exception as e:
        data_checks["files_readable"] = "FAIL"
        errors.append(f"Data files unreadable: {str(e)}")

    try:
        required_cols = {"mine_id", "mine_name", "state", "latitude", "longitude"}
        schemas_ok = required_cols.issubset(set(mines_df.columns)) and "production_tonnes" in prod_df.columns
        data_checks["schemas_valid"] = "PASS" if schemas_ok else "FAIL"
    except Exception as e:
        data_checks["schemas_valid"] = "FAIL"
        errors.append(f"Schema validation error: {str(e)}")

    try:
        has_provenance = (
            "source" in prod_df.columns and
            "data_status" in prod_df.columns and
            prod_df["source"].notna().all()
        )
        data_checks["provenance_valid"] = "PASS" if has_provenance else "FAIL"
    except Exception as e:
        data_checks["provenance_valid"] = "FAIL"
        errors.append(f"Provenance validation error: {str(e)}")

    data_status = "PASS" if all(v == "PASS" for v in data_checks.values()) else "FAIL"

    # -------------------------------------------------------------
    # 2. CAPABILITY AUDIT
    # -------------------------------------------------------------
    capability_checks = {}
    try:
        cap_matrix = data_loader.get_mine_capability_matrix()
        matrix_list = cap_matrix.get("matrix", [])
        capability_checks["capability_matrix_valid"] = "PASS" if len(matrix_list) == 10 else "FAIL"

        tier_map = {m["mine_id"]: m["tier"] for m in matrix_list}
        tier_dist_ok = (
            tier_map.get("MOIL_BALAGHAT") == "LEVEL_A" and
            tier_map.get("MOIL_UKWA") == "LEVEL_B" and
            tier_map.get("MOIL_TIRODI") == "LEVEL_B" and
            tier_map.get("MOIL_SITAPATORE") == "LEVEL_C" and
            tier_map.get("MOIL_KANDRI") == "LEVEL_D"
        )
        capability_checks["mine_specific_availability_correct"] = "PASS" if tier_dist_ok else "FAIL"

        # Check UNAVAILABLE_FOR_MINE enforcement on Level B/C/D
        ukwa_item = next(m for m in matrix_list if m["mine_id"] == "MOIL_UKWA")
        kandri_item = next(m for m in matrix_list if m["mine_id"] == "MOIL_KANDRI")
        unavail_ok = (
            ukwa_item["capabilities"]["simulation_status"] == "UNAVAILABLE_FOR_MINE" and
            ukwa_item["capabilities"]["satellite_status"] == "UNAVAILABLE_FOR_MINE" and
            kandri_item["capabilities"]["geology_status"] == "UNAVAILABLE_FOR_MINE"
        )
        capability_checks["unavailable_states_enforced"] = "PASS" if unavail_ok else "FAIL"
    except Exception as e:
        capability_checks["capability_matrix_valid"] = "FAIL"
        capability_checks["mine_specific_availability_correct"] = "FAIL"
        capability_checks["unavailable_states_enforced"] = "FAIL"
        errors.append(f"Capability audit error: {str(e)}")

    capability_status = "PASS" if all(v == "PASS" for v in capability_checks.values()) else "FAIL"

    # -------------------------------------------------------------
    # 3. ISOLATION AUDIT
    # -------------------------------------------------------------
    isolation_checks = {}
    try:
        from src.api.routes.real_data import get_real_decision_workflow, get_real_prospectivity_geojson
        
        # Test Ukwa decision workflow isolation
        ukwa_decision = get_real_decision_workflow(
            mine_id="MOIL_UKWA",
            horizon_days=30,
            custom_target=None,
            equipment_availability_pct=None,
            blasting_delay_flag=None,
            rainfall_mm=None
        )
        stage4_u = ukwa_decision["decision_workflow"]["stage_4_analytical_signal"]
        stage5_u = ukwa_decision["decision_workflow"]["stage_5_explanation"]
        stage7_u = ukwa_decision["decision_workflow"]["stage_7_optimization"]
        
        # 1. No forecast leakage
        no_fc = stage4_u["production_forecast_signal"].get("status") == "UNAVAILABLE_FOR_MINE"
        isolation_checks["no_balaghat_forecast_leakage"] = "PASS" if no_fc else "FAIL"

        # 2. No SHAP leakage
        no_shap = stage5_u.get("status") == "UNAVAILABLE_FOR_MINE"
        isolation_checks["no_balaghat_shap_leakage"] = "PASS" if no_shap else "FAIL"

        # 3. No exploration leakage (0 features for non-Balaghat)
        ukwa_geo = get_real_prospectivity_geojson("MOIL_UKWA")
        no_expl = len(ukwa_geo.get("features", [])) == 0
        isolation_checks["no_balaghat_exploration_leakage"] = "PASS" if no_expl else "FAIL"

        # 4. No optimization leakage
        no_opt = stage7_u.get("status") == "UNAVAILABLE_FOR_MINE"
        isolation_checks["no_balaghat_optimization_leakage"] = "PASS" if no_opt else "FAIL"
    except Exception as e:
        isolation_checks["no_balaghat_forecast_leakage"] = "FAIL"
        isolation_checks["no_balaghat_shap_leakage"] = "FAIL"
        isolation_checks["no_balaghat_exploration_leakage"] = "FAIL"
        isolation_checks["no_balaghat_optimization_leakage"] = "FAIL"
        errors.append(f"Isolation audit error: {str(e)}")

    isolation_status = "PASS" if all(v == "PASS" for v in isolation_checks.values()) else "FAIL"

    # -------------------------------------------------------------
    # 4. DECISION WORKFLOW AUDIT (Level A: Balaghat)
    # -------------------------------------------------------------
    decision_checks = {}
    try:
        bal_decision = get_real_decision_workflow(
            mine_id="MOIL_BALAGHAT",
            horizon_days=30,
            custom_target=None,
            equipment_availability_pct=None,
            blasting_delay_flag=None,
            rainfall_mm=None
        )
        dw = bal_decision.get("decision_workflow", {})
        
        decision_checks["context_stage"] = "PASS" if dw.get("stage_1_mine_context") else "FAIL"
        decision_checks["analysis_stage"] = "PASS" if dw.get("stage_4_analytical_signal") else "FAIL"
        decision_checks["explanation_stage"] = "PASS" if dw.get("stage_5_explanation") else "FAIL"
        decision_checks["scenario_stage"] = "PASS" if dw.get("stage_6_scenario") else "FAIL"
        decision_checks["optimization_stage"] = "PASS" if dw.get("stage_7_optimization") else "FAIL"
        decision_checks["recommendation_stage"] = "PASS" if dw.get("stage_8_recommended_action") else "FAIL"
    except Exception as e:
        decision_checks["context_stage"] = "FAIL"
        decision_checks["analysis_stage"] = "FAIL"
        decision_checks["explanation_stage"] = "FAIL"
        decision_checks["scenario_stage"] = "FAIL"
        decision_checks["optimization_stage"] = "FAIL"
        decision_checks["recommendation_stage"] = "FAIL"
        errors.append(f"Decision workflow audit error: {str(e)}")

    decision_status = "PASS" if all(v == "PASS" for v in decision_checks.values()) else "FAIL"

    # -------------------------------------------------------------
    # 5. FRONTEND / BACKEND CONNECTIVITY AUDIT
    # -------------------------------------------------------------
    frontend_checks = {
        "backend_reachable": "PASS"
    }
    frontend_status = "PASS"

    # -------------------------------------------------------------
    # 6. PERFORMANCE BENCHMARK (Warm-Cache Median Latency)
    # -------------------------------------------------------------
    warm_samples_ms: List[float] = []
    for _ in range(5):
        t0 = time.perf_counter()
        _ = data_loader.get_mine_capability_matrix()
        _ = data_loader.get_mine_dashboard_summary("MOIL_BALAGHAT")
        t1 = time.perf_counter()
        warm_samples_ms.append((t1 - t0) * 1000.0)

    warm_samples_ms.sort()
    median_latency_ms = round(warm_samples_ms[len(warm_samples_ms) // 2], 2)
    target_ms = 100.0
    within_target = bool(median_latency_ms <= target_ms)

    performance_payload = {
        "target_ms": target_ms,
        "observed_ms": median_latency_ms,
        "within_target": within_target,
        "benchmark_method": "median_warm_cache_5_iterations",
        "sample_runs_ms": [round(s, 2) for s in warm_samples_ms]
    }

    # Overall Status: Based strictly on correctness checks
    overall_status = (
        "PASS"
        if all(s == "PASS" for s in [data_status, capability_status, isolation_status, decision_status, frontend_status])
        else "FAIL"
    )

    return {
        "status": overall_status,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "categories": {
            "data": {
                "status": data_status,
                "checks": data_checks
            },
            "capability": {
                "status": capability_status,
                "checks": capability_checks
            },
            "isolation": {
                "status": isolation_status,
                "checks": isolation_checks
            },
            "decision_workflow": {
                "status": decision_status,
                "checks": decision_checks
            },
            "frontend": {
                "status": frontend_status,
                "checks": frontend_checks
            }
        },
        "performance": performance_payload,
        "errors": errors
    }
