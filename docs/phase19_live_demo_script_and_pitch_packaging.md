# TATTVA — Phase 19: Live Demonstration Script & Technical Pitch Packaging

## Executive Summary

**TATTVA** (Geospatial Mining Intelligence Platform for the Central India Manganese Belt) is engineered for high-stakes technical evaluation before statutory authorities and hackathon juries. Phase 19 provides the turnkey presentation engine, interactive presenter teleprompter (Presenter HUD), hierarchical pre-flight verification system, and publication-grade juror defense framework.

This document establishes the **authoritative 5-minute timed presentation script**, mathematical defensibility rationale, and objection-handling strategies across all 10 MOIL statutory mines.

---

## 1. Zero Demo-Only Shortcuts Rule (Public Pathway Parity)

In strict adherence to Phase 19 scientific governance:
- **No Mock Bypasses**: The demonstration system introduces zero demo-only backend shortcuts or mocked calculations.
- **100% Pathway Parity**: Every action in the presenter teleprompter (mine transitions, raster layer toggling, scenario perturbations, and PuLP MILP solver invocations) executes the identical public production APIs and state management paths used during standard operator interaction:
  - Switching to Ukwa dispatches `setSelectedRealMineId('MOIL_UKWA')`, which invokes `GET /api/real/mine-dashboard/MOIL_UKWA` and `GET /api/real/decision/MOIL_UKWA`, dynamically computing `UNAVAILABLE_FOR_MINE`.
  - Running scenario adjustments executes `POST /api/real/production/reconciliation` with active constraint matrices.
  - Displaying exploration priority fetches the real 27,720-cell GeoJSON from `GET /api/real/prospectivity/MOIL_BALAGHAT/geojson`.
- **Backend Demo Router Role**: Restricted strictly to providing presentation metadata (teleprompter text, timing cues, expected step assertions) and pre-flight health diagnostics.

---

## 2. Authoritative 12-Step Demonstration Sequence

Sourced directly from [config/demo_config.py](file:///g:/Tattvam/TATTVA/config/demo_config.py):

| Step | Target Mine / Scope | Step Title & Purpose | Target View / Component | Expected Capability / Status | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `MOIL_BALAGHAT` (Global) | Application Initialization & Belt Context | `OverviewPage` / Map Header | `LEVEL_A` (10-Mine Registry) | Loads 10 statutory MOIL mines, WGS84 coordinate pins, and Company reported totals. |
| **2** | `MOIL_BALAGHAT` | Real Remote Sensing & Terrain | `MapPage` (Digital Mine) | `LEVEL_A` (`REAL`) | 30m Sentinel-2 L2A multispectral indices (NDVI, clay, iron) & Copernicus DEM. |
| **3** | `MOIL_BALAGHAT` | Phase 9B Exploration Priority Surface | `MapPage` (Real Prospectivity) | `LEVEL_A` (`EXPERIMENTAL`) | 27,720-cell unsupervised anomaly ensemble rankings & Bharweli shaft anchor. |
| **4** | `MOIL_BALAGHAT` | Authoritative DSR Evidence & Geology | `MapPage` (DSR Evidence) | `LEVEL_A` (`SOURCE-DERIVED`) | Balaghat DSR 2022 Mansar Formation stratigraphy, drilling counts, and UNFC reserves. |
| **5** | `MOIL_BALAGHAT` | Production Forecaster & Explainability | `ForecastPage` / `ExplainPage` | `LEVEL_A` (`SIMULATION` + `SHAP`) | 30-day LightGBM quantile forecast & Tree-SHAP non-causal feature attribution rankings. |
| **6** | `MOIL_BALAGHAT` | Interactive What-If Scenario Sandbox | `SimulatePage` / Recon | `LEVEL_A` (`SIMULATION`) | Perturb availability (88%), rain (12.5mm); compute recovery delta. |
| **7** | `MOIL_BALAGHAT` | PuLP MILP Decision Optimization | `ActionsPage` / Optimization | `LEVEL_A` (`OPTIMIZATION`) | Solves constrained MILP model under Balaghat DSR statutory recovery/stowing caps. |
| **8** | `MOIL_BALAGHAT` | Decision Limitations & Provenance | `ResourcesPage` / Stage 9 | `LEVEL_A` (`PROVENANCE`) | Inspects 7-tier provenance taxonomy & non-causal scientific disclaimers. |
| **9** | `MOIL_UKWA` | Switch to Ukwa (Level B Degradation) | `MapPage` / Overview | `LEVEL_B` (`PARTIAL`) | DSR geology/constraints active; exploration & simulation are `UNAVAILABLE_FOR_MINE`. |
| **10** | `MOIL_SITAPATORE`| Switch to Sitapatore (Level C Degradation) | `MapPage` / Overview | `LEVEL_C` (`CONTEXT_ONLY`) | DSR stratigraphy/EC cap active; exploration, simulation, & optimization `UNAVAILABLE_FOR_MINE`. |
| **11** | `MOIL_KANDRI` | Switch to Kandri (Level D Degradation) | `MapPage` / Overview | `LEVEL_D` (`REGISTRY_ONLY`) | Audited WGS84 coordinates active; MP DSR, exploration, & simulation `UNAVAILABLE_FOR_MINE`. |
| **12** | `MOIL_BALAGHAT` | Return to Balaghat (Clean Reinstatement)| `MapPage` / Full Stack | `LEVEL_A` (`REINSTATEMENT`) | Clean state restoration; proves zero cross-mine leakage or layer residue. |

---

## 3. 5-Minute Timed Speaker Script & Cue Cards

### **Step 1: Application Initialization & Belt Context (0:00 – 0:25)**
- **Target Screen**: `OverviewPage` (`/`)
- **Action**: Load TATTVA dashboard with default Balaghat mine context; inspect 10-mine MOIL statutory registry.
- **Verbatim Speaker Delivery**:
  > *"Welcome to TATTVA. We begin across the Central India Manganese Belt with 10 statutory MOIL mines, anchored by verified WGS84 coordinate audits and company-level reported production."*
- **Screen State**: Regional map displays 10 statutory MOIL pins across MP and Maharashtra; company historical totals reflect FY16–FY26 reported figures.

### **Step 2: Balaghat Real Remote Sensing & Terrain (0:25 – 0:50)**
- **Target Screen**: `MapPage` (`/mine-map?mine=MOIL_BALAGHAT`)
- **Action**: Inspect 30m Sentinel-2 L2A multispectral indices (NDVI, iron oxide, clay) and Copernicus DEM terrain models.
- **Verbatim Speaker Delivery**:
  > *"In the Digital Mine view, we inspect real 30m Sentinel-2 Level-2A multispectral band ratios and Copernicus DEM topography over the Balaghat Area of Interest."*
- **Screen State**: True Color and false color Sentinel-2 rasters render over Balaghat lease extents with 30m Copernicus elevation overlays.

### **Step 3: Phase 9B Exploration Priority Surface (0:50 – 1:15)**
- **Target Screen**: `MapPage` (`/mine-map?mine=MOIL_BALAGHAT`)
- **Action**: Toggle Phase 9B unsupervised ensemble surface (27,720 raster cells) and inspect top-tier anomaly clusters.
- **Verbatim Speaker Delivery**:
  > *"Here is our Phase 9B exploration surface: 27,720 cells ranked via an unsupervised ensemble combining Isolation Forest, Mahalanobis distance, and Bharweli shaft portal similarity."*
- **Screen State**: 27,720-cell grid renders with red/amber priority hotspots along the Mansar reef strike; Bharweli shaft portal shows reference anchor similarity 1.000.

### **Step 4: Authoritative DSR Evidence & Geology (1:15 – 1:40)**
- **Target Screen**: `MapPage` (`/mine-map?mine=MOIL_BALAGHAT`)
- **Action**: Review Balaghat DSR 2022 Mansar Formation stratigraphy, aggregate exploratory drilling, and UNFC reserve categories.
- **Verbatim Speaker Delivery**:
  > *"We integrate authoritative District Survey Report (DSR 2022) data: Mansar Formation gondite and braunite reef stratigraphy, drilling counts, and UNFC reserve estimates."*
- **Screen State**: Geological reference panel opens showing Sausar Group lithology, braunite reefs, and UNFC 111/121 reserve summaries.

### **Step 5: Production Forecaster & Root-Cause Explainability (1:40 – 2:10)**
- **Target Screen**: `ForecastPage` (`/forecast?mine=MOIL_BALAGHAT`)
- **Action**: Inspect 30-day LightGBM quantile forecast and Tree-SHAP non-causal feature attribution ranking.
- **Verbatim Speaker Delivery**:
  > *"Moving to operational intelligence, our LightGBM model forecasts daily production with calibrated quantiles (P10, P50, P90), explained via Tree-SHAP attributions."*
- **Screen State**: Production chart renders P10–P90 uncertainty envelopes; Tree-SHAP feature importance ranks blasting delay, equipment availability, and historical trend.

### **Step 6: Interactive What-If Scenario Sandbox (2:10 – 2:40)**
- **Target Screen**: `SimulatePage` (`/simulate?mine=MOIL_BALAGHAT`)
- **Action**: Perturb operational parameters (availability 88%, rain 12.5mm) and evaluate simulated recovery delta.
- **Verbatim Speaker Delivery**:
  > *"In the scenario sandbox, we perturb equipment availability to 88% and rainfall to 12.5mm to evaluate simulated operational variance in real time."*
- **Screen State**: Scenario reconciliation computes simulated production delta (-842 tonnes shortfall) with immediate variance attribution.

### **Step 7: PuLP MILP Decision Optimization (2:40 – 3:10)**
- **Target Screen**: `ActionsPage` (`/actions?mine=MOIL_BALAGHAT`)
- **Action**: Solve constrained MILP model under Balaghat DSR statutory constraints (recovery, stowing ratio, EC caps).
- **Verbatim Speaker Delivery**:
  > *"When targets show shortfall, TATTVA invokes a Mixed-Integer Linear Program (PuLP MILP) to select recovery actions satisfying statutory EC and stowing constraints."*
- **Screen State**: Solver output displays status `Optimal` with 3 ranked dispatch actions (Blasting Reschedule, Excavator Redeployment, Expedited Maintenance).

### **Step 8: Decision Limitations & Provenance Transparency (3:10 – 3:40)**
- **Target Screen**: `ResourcesPage` (`/resources?mine=MOIL_BALAGHAT`)
- **Action**: Inspect structured limitations disclosure (7-tier provenance taxonomy and zero scientific overreach guarantees).
- **Verbatim Speaker Delivery**:
  > *"Transparency is core to TATTVA. We disclose a 7-tier provenance taxonomy and explicit scientific boundaries: what TATTVA knows, derives, simulates, and refuses to claim."*
- **Screen State**: 7-tier provenance taxonomy and scientific limitation cards render with explicit non-causal disclaimers.

### **Step 9: Switch to Ukwa (Level B Degradation) (3:40 – 4:05)**
- **Target Screen**: `MapPage` (`/mine-map?mine=MOIL_UKWA`)
- **Action**: Demonstrate graceful degradation: DSR geology and mining strategy constraints load; exploration surface & simulation cleanly unmount (`UNAVAILABLE_FOR_MINE`).
- **Verbatim Speaker Delivery**:
  > *"Now observe multi-mine isolation: switching to Ukwa Mine loads its DSR geology and mining strategy constraints, while exploration rasters and operational simulation gracefully degrade to UNAVAILABLE_FOR_MINE."*
- **Screen State**: Dynamic badge switches to `LEVEL_B`; exploration and simulation cards display amber warning `UNAVAILABLE_FOR_MINE` with zero Balaghat data leakage.

### **Step 10: Switch to Sitapatore (Level C Degradation) (4:05 – 4:25)**
- **Target Screen**: `MapPage` (`/mine-map?mine=MOIL_SITAPATORE`)
- **Action**: Demonstrate contextual intelligence: DSR stratigraphy and EC cap load; exploration, simulation, and optimization are `UNAVAILABLE_FOR_MINE`.
- **Verbatim Speaker Delivery**:
  > *"Switching to Sitapatore Mine shows Level C Contextual Intelligence: regional stratigraphy and EC clearance limits are active, while optimization and simulation remain UNAVAILABLE_FOR_MINE."*
- **Screen State**: Dynamic badge switches to `LEVEL_C`; optimization displays `UNAVAILABLE_FOR_MINE` due to absence of operational geometry constraints.

### **Step 11: Switch to Kandri (Level D Degradation) (4:25 – 4:45)**
- **Target Screen**: `MapPage` (`/mine-map?mine=MOIL_KANDRI`)
- **Action**: Demonstrate registry-only mode: Audited WGS84 coordinates and company production load; MP DSR, exploration, and simulation are `UNAVAILABLE_FOR_MINE`.
- **Verbatim Speaker Delivery**:
  > *"For Kandri in Maharashtra, TATTVA operates in Level D Registry-Only mode: displaying audited WGS84 coordinates and company production, with all MP DSR modules unmounted."*
- **Screen State**: Dynamic badge switches to `LEVEL_D`; MP DSR data cleanly unmounts with verified cross-state boundary isolation.

### **Step 12: Return to Balaghat (Clean Reinstatement) (4:45 – 5:00)**
- **Target Screen**: `MapPage` (`/mine-map?mine=MOIL_BALAGHAT`)
- **Action**: Return to Balaghat; verify 100% state restoration, zero cross-mine contamination, and reproducible model outputs.
- **Verbatim Speaker Delivery**:
  > *"Finally, returning to Balaghat demonstrates complete state reinstatement: all Level A layers, models, and optimization contracts restore cleanly with 100% mathematical fidelity."*
- **Screen State**: Balaghat Level A full workflow reinstates cleanly, proving zero memory leaks or layer residue.

---

## 4. Technical Juror Defense & Objection Handling Guide

| Juror Objection / Skepticism | Technical Defense & Mathematical Rationale |
| :--- | :--- |
| **"Why is there only one positive anchor in the exploration model?"** | In mineral exploration, verified surface portals with published geospatial coordinates represent ground truth infrastructure anchors. Bharweli (`GRID-13860`) is our reference positive vector. We evaluate 35 proximal pit cells under Configuration B, demonstrating 97.2% rank correlation with single-anchor results. Anchor similarity equals 1.000 by mathematical construction, not independent model discovery. |
| **"Why do you not claim mineralization probability?"** | Ground truth negative drilling labels (confirmed barren assay logs) are not available in public mining records. Supervised binary classification requires true negatives; without them, claiming a calibrated "probability of mineralization" is scientifically false. TATTVA uses an unsupervised anomaly ensemble providing relative priority rankings. |
| **"Why is operational simulation UNAVAILABLE_FOR_MINE for Ukwa?"** | Operational shift simulation requires mine-specific equipment telemetry, face geometry, and shift logs. Ukwa has published DSR geological context and environmental clearance caps, but lacks published operational shift telemetry. Rather than falsifying data by copying Balaghat/Block-A parameters, TATTVA enforces strict scientific honesty via `UNAVAILABLE_FOR_MINE`. |
| **"How is company-level reported production isolated from mine-level targets?"** | MOIL statutory annual report production (FY16–FY26) is audited company-level aggregate context. It is never allocated arbitrarily across the 10 mines or used as a synthetic mine target. Operational targets exist strictly in the micro operational simulation layer. |
| **"Does Tree-SHAP prove that blasting delays cause production drops?"** | No. Tree-SHAP explains mathematical variance contribution within the trained LightGBM model under historical feature correlations. It provides decision support explainability, not proven physical or mechanical causality. |
| **"Are PuLP MILP optimization recommendations binding on mine managers?"** | No. PuLP MILP solves for mathematical optimality within statutory bounds (85% recovery factor, 1:1.2 stowing ratio, EC caps). Recommendations serve as prioritized decision support; operational dispatch remains subject to mine manager authorization. |
| **"How do you prevent cross-mine data leakage during rapid switching?"** | State isolation is enforced at both API and UI layers: API endpoints validate mine ID parameters and return strictly mine-scoped payloads. Frontend state machines unmount prior layers and popups before binding the new mine context. Verified by automated bidirectional transition tests ($A \to B \to C \to D \to A$). |
| **"What coordinate standard is used across all 10 mines?"** | All 10 MOIL mines are audited under WGS84 geographic coordinates (EPSG:4326) and projected to UTM Zone 44N (EPSG:32644) for Euclidean distance and area computations. Coordinates are classified into statutory surveyed portals, lease centroids, and map-derived references. |

---

## 5. Hierarchical Pre-Flight Health Architecture

The `/api/real/demo/preflight` endpoint evaluates 17 discrete verification checks across 6 core categories:

```
DATA
 ├── files_readable (Mines CSV, GeoJSON, Production CSV, DSR Tables)
 ├── schemas_valid (Mandatory columns, geometry properties)
 └── provenance_valid (Audit sources, statutory citations)

CAPABILITY
 ├── capability_matrix_valid (10 registered MOIL mines)
 ├── mine_specific_availability_correct (Levels A, B, C, D distribution)
 └── unavailable_states_enforced (UNAVAILABLE_FOR_MINE semantics)

ISOLATION
 ├── no_balaghat_forecast_leakage (Ukwa/Kandri forecast status UNAVAILABLE_FOR_MINE)
 ├── no_balaghat_shap_leakage (Level B/C/D SHAP status UNAVAILABLE_FOR_MINE)
 ├── no_balaghat_exploration_leakage (0 features in non-Balaghat GeoJSON)
 └── no_balaghat_optimization_leakage (Optimization status UNAVAILABLE_FOR_MINE)

DECISION WORKFLOW
 ├── context_stage (Stage 1 mine metadata & concession scope)
 ├── analysis_stage (Stage 4 analytical signal)
 ├── explanation_stage (Stage 5 Tree-SHAP attribution)
 ├── scenario_stage (Stage 6 scenario perturbation)
 ├── optimization_stage (Stage 7 PuLP MILP solver)
 └── recommendation_stage (Stage 8 recommended actions)

FRONTEND
 └── backend_reachable (FastAPI API V1 connectivity)

PERFORMANCE
 └── measured_latency (Median warm-cache latency over 5 iterations)
```

---

## 6. Verification and Test Results

- **Automated Test Suite**: [tests/test_phase19_demo_execution.py](file:///g:/Tattvam/TATTVA/tests/test_phase19_demo_execution.py)
  - 19 / 19 passed (100%) in 14.04s.
- **Full Pytest Suite**: 156 / 156 passed (100%) across all modules.
- **Frontend Production Build**: Built in 20.74s with 0 errors.
- **Pre-Flight Health Telemetry**: Status `PASS`, observed latency ~57.8ms (within 100ms target).
