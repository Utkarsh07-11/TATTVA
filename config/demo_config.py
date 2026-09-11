"""
Deterministic Demonstration Configuration for TATTVA (Phase 19)
Single Authoritative Source of Truth for the 12-Step Demonstration Workflow.
References existing real, source-derived, and simulation datasets without fabricating live data.
"""

from typing import Dict, Any, List

DEMO_CONFIG: Dict[str, Any] = {
    "version": "2.0.0",
    "phase": "Phase 19 Live Demonstration Script & Technical Pitch Packaging",
    "primary_demo_mine": "MOIL_BALAGHAT",
    "default_horizon_days": 30,
    "default_view": "mine_map",
    "total_presentation_time_sec": 300,
    "default_scenario": {
        "equipment_availability_pct": 88.0,
        "blasting_delay_flag": 0,
        "rainfall_mm": 12.5,
        "custom_target": 10000.0
    },
    "demonstration_path": [
        {
            "step": 1,
            "step_id": 1,
            "title": "Application Initialization & Belt Context",
            "mine_id": "MOIL_BALAGHAT",
            "tier": "LEVEL_A",
            "target_screen": "overview",
            "action_type": "NAVIGATE_VIEW",
            "action": "Load TATTVA dashboard with default Balaghat mine context; inspect 10-mine MOIL statutory registry.",
            "timing_target_sec": 25,
            "speaker_notes": "Welcome to TATTVA. We begin across the Central India Manganese Belt with 10 statutory MOIL mines, anchored by verified WGS84 coordinate audits and company-level reported production.",
            "juror_defense_notes": "All 10 mine locations are audited against statutory IBM filings and District Survey Reports, classified by coordinate precision (statutory surveyed vs centroid vs map reference).",
            "governance_disclosure": "Company reported production is macro historical context (FY16-FY26) and is never allocated arbitrarily to individual mines.",
            "expected_capability": "LEVEL_A",
            "expected_api_response": {
                "total_mines": 10,
                "data_status": "real"
            }
        },
        {
            "step": 2,
            "step_id": 2,
            "title": "Balaghat Real Remote Sensing & Terrain",
            "mine_id": "MOIL_BALAGHAT",
            "tier": "LEVEL_A",
            "target_screen": "mine_map",
            "action_type": "TOGGLE_LAYER",
            "action": "Inspect 30m Sentinel-2 L2A multispectral indices (NDVI, iron oxide, clay) and Copernicus DEM terrain models.",
            "timing_target_sec": 50,
            "speaker_notes": "In the Digital Mine view, we inspect real 30m Sentinel-2 Level-2A multispectral band ratios and Copernicus DEM topography over the Balaghat Area of Interest.",
            "juror_defense_notes": "Earth observation rasters are calibrated surface reflectances and GLO-30 elevations; they provide geophysical context and are not labeled as subsurface drillhole certainty.",
            "governance_disclosure": "Remote sensing rasters reflect surface spectral and elevation characteristics, requiring ground geological validation.",
            "expected_capability": "LEVEL_A",
            "expected_api_response": {
                "sentinel2_available": True,
                "dem_available": True
            }
        },
        {
            "step": 3,
            "step_id": 3,
            "title": "Phase 9B Exploration Priority Surface",
            "mine_id": "MOIL_BALAGHAT",
            "tier": "LEVEL_A",
            "target_screen": "mine_map",
            "action_type": "TOGGLE_LAYER",
            "action": "Toggle Phase 9B unsupervised ensemble surface (27,720 raster cells) and inspect top-tier anomaly clusters.",
            "timing_target_sec": 75,
            "speaker_notes": "Here is our Phase 9B exploration surface: 27,720 cells ranked via an unsupervised ensemble combining Isolation Forest, Mahalanobis distance, and Bharweli shaft portal similarity.",
            "juror_defense_notes": "This is a relative priority ranking heuristic, NOT a probability of mineralization. Because mineral exploration lacks confirmed negative drilling logs in the public domain, the background is strictly unlabeled.",
            "governance_disclosure": "Anchor similarity equals 1.000 at the Bharweli shaft portal by mathematical definition as reference anchor, not as independent discovery validation.",
            "expected_capability": "EXPERIMENTAL",
            "expected_api_response": {
                "total_cells": 27720,
                "anchor_similarity_max": 1.0
            }
        },
        {
            "step": 4,
            "step_id": 4,
            "title": "Authoritative DSR Evidence & Geology",
            "mine_id": "MOIL_BALAGHAT",
            "tier": "LEVEL_A",
            "target_screen": "mine_map",
            "action_type": "TOGGLE_LAYER",
            "action": "Review Balaghat DSR 2022 Mansar Formation stratigraphy, aggregate exploratory drilling, and UNFC reserve categories.",
            "timing_target_sec": 100,
            "speaker_notes": "We integrate authoritative District Survey Report (DSR 2022) data: Mansar Formation gondite and braunite reef stratigraphy, drilling counts, and UNFC reserve estimates.",
            "juror_defense_notes": "All geological stratigraphy and UNFC reserve figures originate directly from the statutory Balaghat DSR 2022 and are cited with source page and table metadata.",
            "governance_disclosure": "Stratigraphic lithologies are source-derived regional reference descriptions, preserving published reserve categories.",
            "expected_capability": "SOURCE-DERIVED",
            "expected_api_response": {
                "dsr_geology_available": True,
                "unfc_reserves_available": True
            }
        },
        {
            "step": 5,
            "step_id": 5,
            "title": "Production Forecaster & Root-Cause Explainability",
            "mine_id": "MOIL_BALAGHAT",
            "tier": "LEVEL_A",
            "target_screen": "forecast",
            "action_type": "NAVIGATE_VIEW",
            "action": "Inspect 30-day LightGBM quantile forecast and Tree-SHAP non-causal feature attribution ranking.",
            "timing_target_sec": 130,
            "speaker_notes": "Moving to operational intelligence, our LightGBM model forecasts daily production with calibrated quantiles (P10, P50, P90), explained via Tree-SHAP attributions.",
            "juror_defense_notes": "SHAP feature attributions describe mathematical model variance contributions, not physical causality. Operational data is calibrated for Block A telemetry.",
            "governance_disclosure": "Production logs are operational shift simulations for Block A; quantiles capture historical variability, not deterministic guarantees.",
            "expected_capability": "SIMULATION",
            "expected_api_response": {
                "forecast_model": "LightGBM Quantile Regressor",
                "shap_available": True
            }
        },
        {
            "step": 6,
            "step_id": 6,
            "title": "Interactive What-If Scenario Sandbox",
            "mine_id": "MOIL_BALAGHAT",
            "tier": "LEVEL_A",
            "target_screen": "simulate",
            "action_type": "RUN_SCENARIO",
            "action": "Perturb operational parameters (availability 88%, rain 12.5mm) and evaluate simulated recovery delta.",
            "timing_target_sec": 160,
            "speaker_notes": "In the scenario sandbox, we perturb equipment availability to 88% and rainfall to 12.5mm to evaluate simulated operational variance in real time.",
            "juror_defense_notes": "The sandbox allows dispatchers to stress-test shift plans without modifying baseline forecasts; delta calculations are deterministically computed.",
            "governance_disclosure": "Scenario outputs represent mathematical sensitivity responses, not live sensor streams.",
            "expected_capability": "SIMULATION",
            "expected_api_response": {
                "scenario_executed": True,
                "baseline_vs_scenario_isolated": True
            }
        },
        {
            "step": 7,
            "step_id": 7,
            "title": "PuLP MILP Decision Optimization",
            "mine_id": "MOIL_BALAGHAT",
            "tier": "LEVEL_A",
            "target_screen": "actions",
            "action_type": "SOLVE_MILP",
            "action": "Solve constrained MILP model under Balaghat DSR statutory constraints (recovery, stowing ratio, EC caps).",
            "timing_target_sec": 190,
            "speaker_notes": "When targets show shortfall, TATTVA invokes a Mixed-Integer Linear Program (PuLP MILP) to select recovery actions satisfying statutory EC and stowing constraints.",
            "juror_defense_notes": "Optimization is bounded by published DSR constraints (85% recovery factor, 1:1.2 hydraulic stowing ratio, EC environmental caps).",
            "governance_disclosure": "The solver produces mathematically optimal allocations within specified bounds; execution remains subject to mine manager authorization.",
            "expected_capability": "OPTIMIZATION",
            "expected_api_response": {
                "solver": "PuLP Mixed-Integer Linear Programming (MILP)",
                "solver_status": "Optimal"
            }
        },
        {
            "step": 8,
            "step_id": 8,
            "title": "Decision Limitations & Provenance Transparency",
            "mine_id": "MOIL_BALAGHAT",
            "tier": "LEVEL_A",
            "target_screen": "resources",
            "action_type": "AUDIT_PROVENANCE",
            "action": "Inspect structured limitations disclosure (7-tier provenance taxonomy and zero scientific overreach guarantees).",
            "timing_target_sec": 220,
            "speaker_notes": "Transparency is core to TATTVA. We disclose a 7-tier provenance taxonomy and explicit scientific boundaries: what TATTVA knows, derives, simulates, and refuses to claim.",
            "juror_defense_notes": "We enforce strict semantic integrity: zero claims of geological certainty, no marketing buzzwords, and clear separation between macro reported data and micro simulation.",
            "governance_disclosure": "All data classifications adhere to the 7-tier taxonomy (REAL, SOURCE-DERIVED, DERIVED, REFERENCE, SIMULATION, EXPERIMENTAL, UNAVAILABLE).",
            "expected_capability": "PROVENANCE",
            "expected_api_response": {
                "provenance_tiers_count": 7,
                "limitations_declared": True
            }
        },
        {
            "step": 9,
            "step_id": 9,
            "title": "Switch to Ukwa (Level B Degradation)",
            "mine_id": "MOIL_UKWA",
            "tier": "LEVEL_B",
            "target_screen": "mine_map",
            "action_type": "SWITCH_MINE",
            "action": "Demonstrate graceful degradation: DSR geology, lease boundaries, and constraints load; exploration surface & simulation cleanly unmount (UNAVAILABLE_FOR_MINE).",
            "timing_target_sec": 245,
            "speaker_notes": "Now observe multi-mine isolation: switching to Ukwa Mine loads its DSR geology and mining strategy constraints, while exploration rasters and operational simulation gracefully degrade to UNAVAILABLE_FOR_MINE.",
            "juror_defense_notes": "Ukwa lacks mine-specific raster features and shift telemetry. We deliberately return UNAVAILABLE_FOR_MINE rather than falsely borrowing Balaghat parameters.",
            "governance_disclosure": "Zero parameter inheritance from Balaghat. Operational simulation and rasters are explicitly refused for Ukwa.",
            "expected_capability": "LEVEL_B",
            "expected_api_response": {
                "tier": "LEVEL_B",
                "simulation_status": "UNAVAILABLE_FOR_MINE",
                "exploration_status": "UNAVAILABLE_FOR_MINE"
            }
        },
        {
            "step": 10,
            "step_id": 10,
            "title": "Switch to Sitapatore (Level C Degradation)",
            "mine_id": "MOIL_SITAPATORE",
            "tier": "LEVEL_C",
            "target_screen": "mine_map",
            "action_type": "SWITCH_MINE",
            "action": "Demonstrate contextual intelligence: DSR stratigraphy and EC cap load; exploration, simulation, and optimization are UNAVAILABLE_FOR_MINE.",
            "timing_target_sec": 265,
            "speaker_notes": "Switching to Sitapatore Mine shows Level C Contextual Intelligence: regional stratigraphy and EC clearance limits are active, while optimization and simulation remain UNAVAILABLE_FOR_MINE.",
            "juror_defense_notes": "Sitapatore has environmental EC limits but no operational mining geometry constraints in DSR records, correctly placing it in Level C.",
            "governance_disclosure": "Contextual intelligence provides verified regulatory reference data without executing unsupported decision engines.",
            "expected_capability": "LEVEL_C",
            "expected_api_response": {
                "tier": "LEVEL_C",
                "optimization_status": "UNAVAILABLE_FOR_MINE"
            }
        },
        {
            "step": 11,
            "step_id": 11,
            "title": "Switch to Kandri (Level D Degradation)",
            "mine_id": "MOIL_KANDRI",
            "tier": "LEVEL_D",
            "target_screen": "mine_map",
            "action_type": "SWITCH_MINE",
            "action": "Demonstrate registry-only mode: Audited WGS84 coordinates and company production load; MP DSR, exploration, and simulation are UNAVAILABLE_FOR_MINE.",
            "timing_target_sec": 280,
            "speaker_notes": "For Kandri in Maharashtra, TATTVA operates in Level D Registry-Only mode: displaying audited WGS84 coordinates and company production, with all MP DSR modules unmounted.",
            "juror_defense_notes": "Because Kandri is in Maharashtra (Nagpur district), Madhya Pradesh DSR documents do not apply. Cross-district data leakage is strictly blocked.",
            "governance_disclosure": "Registry & reference mode displays verified statutory coordinates with zero cross-state DSR contamination.",
            "expected_capability": "LEVEL_D",
            "expected_api_response": {
                "tier": "LEVEL_D",
                "geology_status": "UNAVAILABLE_FOR_MINE",
                "simulation_status": "UNAVAILABLE_FOR_MINE"
            }
        },
        {
            "step": 12,
            "step_id": 12,
            "title": "Return to Balaghat (Clean Reinstatement)",
            "mine_id": "MOIL_BALAGHAT",
            "tier": "LEVEL_A",
            "target_screen": "mine_map",
            "action_type": "SWITCH_MINE",
            "action": "Return to Balaghat; verify 100% state restoration, zero cross-mine contamination, and reproducible model outputs.",
            "timing_target_sec": 300,
            "speaker_notes": "Finally, returning to Balaghat demonstrates complete state reinstatement: all Level A layers, models, and optimization contracts restore cleanly with 100% mathematical fidelity.",
            "juror_defense_notes": "This bidirectional transition test (A -> B -> C -> D -> A) proves complete state isolation and memory cleanup with zero leftover layer residue.",
            "governance_disclosure": "State restoration reinstates verified model outputs deterministically.",
            "expected_capability": "LEVEL_A",
            "expected_api_response": {
                "tier": "LEVEL_A",
                "decision_workflow_status": "FULL_DECISION_WORKFLOW"
            }
        }
    ]
}
