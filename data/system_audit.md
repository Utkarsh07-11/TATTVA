# TATTVA — Full System & Architecture Audit Report

**Date:** September 2026  
**Auditor:** Project TATTVA Core Agentic System  
**Audit Scope:** Full codebase audit covering Backend (`src/`), Frontend (`frontend/src/`), Data Repositories (`data/`), Machine Learning Assets (`data/models/`), and Test Suite (`tests/`).  
**Mode:** Read-Only Audit (Zero code, model, dataset, or configuration mutations).

---

# 1. Current Architecture

Project TATTVA is architected as an AI/ML-based mining intelligence and decision-support platform designed for the **Central India Manganese Belt (MOIL Balaghat Operations)**.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FRONTEND (React + Vite + Leaflet)                              │
│  - AppShell / Multi-Page Routing (Overview, Map, Forecast, Explain, Recommendations, Simulate)   │
│  - DigitalMineMap (Leaflet + SoI Sovereign Boundary Overlay + Multi-Basemap Selector)            │
│  - Interactive Visualizations (ApexCharts / Recharts for Quantiles, SHAP Waterfall, Action Cards)│
└──────────────────────────────────────────────▲───────────────────────────────────────────────────┘
                                               │ HTTP / REST API (JSON & GeoJSON)
┌──────────────────────────────────────────────▼───────────────────────────────────────────────────┐
│                                     BACKEND (FastAPI API V1)                                     │
│  - Routes: /mine, /forecast, /explain, /recommend, /prospectivity, /health                       │
│  - Service Layer: Feature Engineering, Geostatistics (IDW), SHAP Explainer, PuLP MILP Optimizer  │
│  - Model Layer: LightGBM Quantile Forecaster (P10/P50/P90), XGBoost Prospectivity Classifier     │
│  - Data Layer: DataLoader with Schema Validators (Pydantic / Custom DataValidator)               │
└──────────────────────────────────────────────▲───────────────────────────────────────────────────┘
                                               │ Filesystem Reads
┌──────────────────────────────────────────────▼───────────────────────────────────────────────────┐
│                                      DATA ARCHITECTURE                                           │
│  ├── REAL DATA (data/real/)                                                                      │
│  │   ├── moil/           → 10-Mine Registry (CSV, GeoJSON), 11-Yr Reported Production Time Series│
│  │   ├── sentinel2/      → Raw 7-Band Sentinel-2 L2A BOA Reflectance Rasters (Balaghat 5x5 km)   │
│  │   ├── dem/            → Raw Copernicus 30m Global DEM COG Subset (Balaghat 5x5 km)           │
│  │   └── geology/        → Provenance & Digitization Audit Reports (GSI/NGDR 64 C/1 Seam)       │
│  ├── DERIVED DATA (data/derived/)                                                                │
│  │   ├── sentinel2/      → Metric UTM44N Analytical GeoTIFFs (NDVI, NDWI, Band Ratios, TCI PNG) │
│  │   ├── dem/            → Metric UTM44N Topographic Rasters (Elevation, Slope, Aspect, Hillshade│
│  │   └── production/     → 10-Year Corporate YoY Growth Time Series                             │
│  └── SYNTHETIC DATA (data/synthetic/ & data/processed/)                                          │
│      ├── production_daily.csv        → 3-Block Shift-Level Daily Production Logs (2023-2026)     │
│      ├── equipment_events.csv        → Heavy Fleet Telemetry & Maintenance Breakdown Events      │
│      ├── drillhole_assay.csv         → 100 Exploration Assay Collars (Mn %, Fe %, SiO2 %)        │
│      ├── satellite_features_grid.csv → 50x50 Synthetic Feature Matrix Grid                      │
│      └── mine_blocks.geojson         → 3 Sub-Pit Operational Mine Blocks (BLOCK_A, B, C)         │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# 2. Implemented Features (Working Today)

1. **Sovereign India Geospatial Basemap Engine:** Leaflet map with integrated Survey of India (SoI) vector boundary rendering and dynamic multi-basemap switching (ESRI Dark Neutral, ESRI Satellite World Imagery, OpenTopoMap, Light Canvas).
2. **Probabilistic Production Forecasting (LightGBM Quantile Regression):** Generates calibrated P10, P50 (median), and P90 forecast curves with rolling-origin temporal validation against Ridge and Naive baselines.
3. **Shortfall Risk & Probability Estimation:** Computes continuous probability of production deficit $P(\text{Production} < \text{Target})$ from quantile uncertainty spread, with automated risk ratings (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
4. **SHAP Operational Root-Cause Attribution:** TreeExplainer decomposition of production shortfalls into intuitive operational categories (Equipment Downtime, Blasting Delays, Monsoon Rainfall, Historical Trend) with plain-language mining narrative generation.
5. **Constrained Mixed-Integer Linear Programming (MILP) Optimizer:** PuLP-powered decision engine that evaluates operational actions (excavator redeployment, shift rescheduling, blast window adjustment) to maximize tonnage recovery under operational cost and feasibility constraints.
6. **Interactive What-If Scenario Sandbox:** Parameter override simulator allowing mine planners to test custom equipment availability %, rainfall mm, and blasting delay scenarios.
7. **Geostatistical Resource Estimation:** Inverse Distance Weighting (IDW) interpolation from drillhole assays to produce grade-tonnage curves and resource summaries across variable cut-off grades ($10\% - 40\% \text{ Mn}$).
8. **Real Data Ingestion & Audit Systems:** Verified pipelines for 10 MOIL statutory mine locations, 7-band Sentinel-2 Level-2A imagery, 30 m Copernicus DEM terrain derivatives, and 11-year audited corporate production records.

---

# 3. Partially Implemented Features

1. **Real Data Consumption in Backend API:** Real datasets (Sentinel-2 rasters, Copernicus DEM, MOIL 10-mine registry, real production series) are stored in `data/real/` and tested in `tests/test_data.py`, but the FastAPI backend (`src/data/loader.py`) still defaults to loading legacy synthetic CSV files (`satellite_features_grid.csv`, `production_daily.csv`).
2. **Real Imagery / DEM Map Overlays on Frontend:** The frontend map displays synthetic prospectivity heatmaps and synthetic mine blocks, but does not yet load or toggle the real Sentinel-2 True Color / NDVI PNGs or Copernicus Hillshade rasters generated in Phase 3 & 4.
3. **MOIL Multi-Mine Switcher:** Frontend map and backend currently center on Balaghat (`BLOCK_A`, `BLOCK_B`, `BLOCK_C`), but do not yet expose a dropdown to switch between the 10 verified MOIL mine locations (`data/real/moil/mines.csv`).
4. **Hierarchical Macro-Micro Production Reconciliation:** Real 11-year company production figures exist in `data/real/moil/production/`, but the production forecasting dashboard currently visualizes only synthetic block-level daily series.

---

# 4. Data Inventory

| Dataset | Real/Synthetic/Derived | Geographic Coverage | Resolution / Granularity | Current Consumer in App |
|---|---|---|---|---|
| `data/real/moil/mines.csv` | **Real** | Central India (MP & Maharashtra) | 10 statutory mine points | `tests/test_data.py` only (Stored) |
| `data/real/moil/mine_locations.geojson` | **Real** | Central India (MP & Maharashtra) | 10 statutory mine points | `tests/test_data.py` only (Stored) |
| `data/real/sentinel2/balaghat/raw/` | **Real** | Balaghat AOI ($5 \times 5 \text{ km}$) | 10 m / 20 m (7 bands) | Python processing scripts & tests |
| `data/derived/sentinel2/balaghat/*.tif` | **Derived (from Real)** | Balaghat AOI ($5 \times 5 \text{ km}$) | 10 m UTM44N analytical rasters | Python processing scripts & tests |
| `data/real/dem/balaghat/raw/` | **Real** | Balaghat AOI ($5 \times 5 \text{ km}$) | 30 m GLO-30 surface model | Python processing scripts & tests |
| `data/derived/dem/balaghat/*.tif` | **Derived (from Real)** | Balaghat AOI ($5 \times 5 \text{ km}$) | 30 m UTM44N terrain rasters | Python processing scripts & tests |
| `data/real/moil/production/production_reported.csv` | **Real** | MOIL corporate & State totals | Annual, quarterly, monthly | `tests/test_data.py` only (Stored) |
| `data/derived/production/moil_annual_yoy_growth.csv` | **Derived (from Real)** | MOIL corporate timeline | 10-year annual YoY growth | Stored analytical artifact |
| `data/synthetic/production_daily.csv` | **Synthetic** | Balaghat Mine (3 blocks) | Daily shift records ($2023-2026$) | `data_loader`, `forecasting`, `explain`, `recommend` |
| `data/synthetic/equipment_events.csv` | **Synthetic** | Balaghat Mine (Fleet EXC/DRL) | Event timestamps & downtime | `data_loader`, `mine/overview` API |
| `data/synthetic/drillhole_assay.csv` | **Synthetic** | Balaghat Mine (100 collars) | Point assays (depth, grades) | `data_loader`, `prospectivity/drillholes` API |
| `data/synthetic/satellite_features_grid.csv` | **Synthetic** | Balaghat Mine grid | $50 \times 50$ point matrix | `data_loader`, `prospectivity_model` |
| `data/synthetic/mine_blocks.geojson` | **Synthetic** | Balaghat Mine ($3 \text{ blocks}$) | 3 Polygon geometries | `data_loader`, `mine/blocks` API, Frontend Map |
| `data/processed/prospectivity_surface.geojson` | **Synthetic** | Balaghat Mine grid | Grid polygons with probabilities | `prospectivity/map` API, Frontend Map |

---

# 5. ML & Analytical Model Inventory

| Model | Purpose | Input Features | Output | Pipeline Status | Training Data Provenance |
|---|---|---|---|---|---|
| **`ProspectivityModel`** (XGBoost Classifier) | Manganese reserve spatial probability estimation | `elevation_m`, `slope_deg`, `aspect_deg`, `ndvi`, `ndwi`, `iron_oxide_index`, `clay_index`, `ferrous_index`, `lst_k` | Probability score $[0.0, 1.0]$ per grid cell | **Trained & Serialized** (`prospectivity_model.pkl`) | **Synthetic** (`drillhole_assay.csv` + `satellite_features_grid.csv`) |
| **`ProductionForecaster`** (LightGBM Quantile Regressors) | Probabilistic 30-day production forecasting | Lags (1, 2, 7, 14, 30), rolling stats, equipment availability, rainfall mm, blasting flags | P10, P50, P90 predicted daily/monthly tonnages | **Trained & Serialized** (`production_forecaster.pkl`) | **Synthetic** (`production_daily.csv`) |
| **`ShortfallRiskEstimator`** (Statistical Gaussian-Quantile) | Shortfall probability and risk rating | Forecast P10, P90 spread, monthly target tonnage | Shortfall probability $\%$, risk category (`LOW` to `CRITICAL`) | **Operational (Rule/Formula)** | Exact mathematical formula applied to forecaster outputs |
| **`ShapExplainerEngine`** (SHAP TreeExplainer) | Root-cause feature attribution | Operational instance features + LightGBM model | Contribution $\%$ and tonnage impact per operational factor | **Operational** | Explains LightGBM predictions on synthetic feature frames |
| **`DecisionOptimizer`** (PuLP MILP Solver) | Optimal action recommendation | Baseline forecast, shortfall, candidate interventions | Ranked action cards with recovery tonnage & cost-benefit scores | **Operational (Linear Optimization)** | Simulates impact using feature modifiers on forecaster |
| **`GeostatisticalResourceEstimator`** (IDW Interpolation) | Spatial grade estimation & resource summary | Drillhole collar assays ($X, Y, \text{Grade}$) | Estimated ore tonnes & average grade at cut-off | **Operational** | Synthetic drillhole assays |

---

# 6. API Inventory

| Method | Endpoint | Description | Return Type | Underlying Data Source |
|---|---|---|---|---|
| `GET` | `/api/health` | System and model runtime status | JSON | In-memory model registry |
| `GET` | `/api/mine/overview` | Mine operational overview, KPI cards, weather | `MineOverviewResponse` | `production_daily.csv`, `equipment_events.csv` |
| `GET` | `/api/mine/blocks` | Mine operational blocks GeoJSON | GeoJSON FeatureCollection | `mine_blocks.geojson` |
| `GET` | `/api/mine/equipment` | Active fleet status and coordinates | JSON Fleet List | In-memory fleet generator (synthetic) |
| `GET` | `/api/prospectivity/map` | Prospectivity probability surface | GeoJSON FeatureCollection | `prospectivity_surface.geojson` |
| `GET` | `/api/prospectivity/drillholes` | Drillhole assay collar points | GeoJSON FeatureCollection | `drillhole_assay.csv` |
| `GET` | `/api/prospectivity/resource-estimate` | IDW resource estimation summary | JSON Summary | `drillhole_assay.csv` |
| `POST` | `/api/forecast/production` | Quantile production forecast | `ForecastResponse` | `ProductionForecaster` (LightGBM) |
| `GET` | `/api/explain/shortfall` | SHAP feature attribution & narrative | `ShortfallExplanationResponse` | `ShapExplainerEngine` (SHAP) |
| `GET` | `/api/recommend/actions` | MILP recommended operational actions | `RecommendationResponse` | `DecisionOptimizer` (PuLP) |
| `POST` | `/api/simulate/scenario` | What-if operational scenario simulation | `SimulationResponse` | `ScenarioSimulator` |

---

# 7. Frontend Inventory

| Component / Page | Visual Elements | Primary Purpose | Current Data Source |
|---|---|---|---|
| `OverviewPage` / `OverviewCards` | KPI cards (Target, Actual, Forecast, Risk Level, Equipment) | Executive mining status dashboard | `/api/mine/overview` |
| `MapPage` / `DigitalMineMap` | Leaflet interactive map, Basemap selector, layer toggles, legend | Geospatial visualization of mine blocks, heatmaps, drillholes, fleet | `/api/mine/blocks`, `/api/prospectivity/map`, `/api/prospectivity/drillholes`, `/api/mine/equipment` |
| `ForecastPage` / `ProductionAnalytics` | Time-series chart (Actual vs. Forecast P10/P50/P90), shortfall gauge | Probabilistic production outlook | `/api/forecast/production` |
| `ExplainPage` / `ExplainabilityPanel` | Factor contribution bars, plain-language narrative, methodology note | Explainable AI (XAI) shortfall root causes | `/api/explain/shortfall` |
| `ActionsPage` / `RecommendationsPanel` | Action cards with recovery tonnage, cost score, feasibility, category | Decision support for shortfall mitigation | `/api/recommend/actions` |
| `SimulatePage` / `WhatIfSandbox` | Parameter sliders (Equipment %, Rain mm, Blasting delay), simulation diff | Interactive what-if planning sandbox | `/api/simulate/scenario` |
| `ResourcesPage` / `ResourceExplorer` | Grade-tonnage curves, cut-off slider, drillhole summary table | Geological exploration and reserve analysis | `/api/prospectivity/resource-estimate` |

---

# 8. Real Data Integration Status

| Real Dataset | Stored on Disk? | Loaded by Backend? | Exposed via API? | Visualized in Frontend? | Used in Analytics? | Used in ML Training? |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **MOIL 10-Mine Registry** (`mines.csv`, `mine_locations.geojson`) | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |
| **Real Sentinel-2 Imagery** (Bands 2, 3, 4, 8, 11, 12, TCI) | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |
| **Derived Sentinel-2 Indices** (NDVI, NDWI, Red/NIR, SWIR/NIR) | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |
| **Real Copernicus 30m DEM** (`elevation`, `slope`, `aspect`, `hillshade`) | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |
| **Real Reported MOIL Production** (`production_reported.csv`) | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |
| **Derived YoY Growth Analytics** (`moil_annual_yoy_growth.csv`) | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |

---

# 9. Synthetic Data Dependencies

The operational and geospatial intelligence pipelines currently rely on synthetic data across five specific layers:

1. **Drillhole Assay Coordinates & Grades (`drillhole_assay.csv`):** 100 collar points generated synthetically to train the XGBoost prospectivity classifier and test IDW geostatistical resource modeling.
2. **Satellite & Terrain Feature Grid (`satellite_features_grid.csv`):** $50 \times 50$ point matrix of synthetic reflectance indices and elevations used as the prediction grid for prospectivity mapping.
3. **Daily Operational Shift Production (`production_daily.csv`):** 4,000 synthetic daily records across `BLOCK_A`, `BLOCK_B`, `BLOCK_C` providing daily variance, rainfall delays, and equipment breakdowns for LightGBM training.
4. **Equipment Telemetry Logs (`equipment_events.csv`):** Simulated excavator and drill breakdown logs powering the fleet health cards.
5. **Mine Block Geometry (`mine_blocks.geojson`):** 3 synthetic polygons delineating mine extraction zones.

---

# 10. Major Technical Gaps

### Priority 0 (Essential for Core Hackathon Integration)
* **P0-1: Connect Real Remote Sensing & Terrain Rasters to Feature Engineering:** Fused feature matrices currently use synthetic `satellite_features_grid.csv`. The spatial feature extractor should extract genuine pixel values directly from `data/derived/sentinel2/balaghat/` and `data/derived/dem/balaghat/`.
* **P0-2: Backend API Exposure of Real MOIL Mines & Real Production Data:** Create dedicated endpoints (e.g. `/api/real/mines`, `/api/real/production/history`, `/api/real/layers`) so the frontend can display real corporate and regional data.
* **P0-3: Frontend Multi-Mine & Real Layer Toggles:** Enable users to view all 10 MOIL mines on the map and toggle real Sentinel-2 True Color / NDVI overlays over the Balaghat AOI.

### Priority 1 (Important for Advanced AI/ML Impact)
* **P1-1: Retrain Prospectivity Classifier on Real Geospatial Rasters:** Sample real NDVI, NDWI, band ratios, elevation, and slope features at known mineralization locations (Bharweli mine deposit anchor and prospect zones) to produce a genuine prospectivity surface.
* **P1-2: Hybrid Macro-Micro Production Model:** Calibrate the micro-simulation operational forecaster against the real 11-year reported annual/quarterly production baseline.
* **P1-3: Real Weather API / Historic Climate Integration:** Replace synthetic daily rainfall with real historical meteorological data for Balaghat District.

### Priority 2 (Enhancement)
* **P2-1: Interactive Digitize Upload for GSI 64 C/1:** Provide an administrative UI tool to upload and auto-georeference scanned GSI map sheets when acquired.
* **P2-2: Multi-Mine Fleet Simulation:** Extend the PuLP MILP optimizer to simulate equipment transfers across multiple MOIL mines (e.g. Balaghat $\leftrightarrow$ Ukwa $\leftrightarrow$ Tirodi).

---

# 11. Recommended Next Development Sequence (8 Concrete Phases)

```mermaid
graph TD
    A[Phase 7: Real Data Loader & API Integration] --> B[Phase 8: Real Remote Sensing Feature Extraction]
    B --> C[Phase 9: Real-Rasters ML Retraining]
    C --> D[Phase 10: Frontend Real Geospatial Map Layers]
    D --> E[Phase 11: Multi-Mine Registry & Switcher UI]
    E --> F[Phase 12: Macro-Micro Production Forecasting Model]
    F --> G[Phase 13: Full System Integration & E2E Validation]
    G --> H[Phase 14: Hackathon Demo Hardening & Polish]
```

1. **Phase 7 — Real Data Loader & API Service Layer:** Update `src/data/loader.py` and create clean API routes (`/api/real/mines`, `/api/real/production`, `/api/real/rasters/summary`) to serve all acquired real datasets.
2. **Phase 8 — Real Geospatial Feature Extractor Pipeline:** Implement raster sampling utilities (`src/features/raster_extractor.py`) to query exact Sentinel-2 reflectance and Copernicus DEM slope/elevation values at arbitrary $(X, Y)$ coordinates in EPSG:32644.
3. **Phase 9 — Retrain Prospectivity Model on Real Remote Sensing Data:** Train the XGBoost prospectivity model using features extracted directly from real Sentinel-2 and DEM rasters, generating an authentic probability surface for the 5 km × 5 km Balaghat AOI.
4. **Phase 10 — Frontend Real Geospatial Overlay Integration:** Add interactive layer toggles in `DigitalMineMap.jsx` to render real Sentinel-2 True Color imagery, NDVI alteration heatmaps, and Copernicus Hillshade relief overlays.
5. **Phase 11 — MOIL 10-Mine Registry Navigation:** Add a multi-mine selector component allowing users to explore all 10 verified MOIL mines across Madhya Pradesh and Maharashtra with full statutory provenance cards.
6. **Phase 12 — Macro-Micro Production Forecasting Engine:** Integrate the real 11-year corporate production time series with the daily LightGBM shift forecaster to deliver hierarchical macro-target reconciliation.
7. **Phase 13 — Full System End-to-End Testing & Verification:** Comprehensive automated integration testing across all APIs, ML pipelines, and frontend views.
8. **Phase 14 — Hackathon Demo Polish & Documentation:** Final UI aesthetic refinement, documentation finalization, and executive demonstration walkthrough preparation.

---

# 12. Final Audit Summary

* **Files Inspected:** Complete inspection of `src/` (12 modules), `frontend/src/` (22 components/pages), `data/` (real, derived, synthetic repositories), and `tests/` (6 test suites).
* **Current Operational State:** All ML pipelines (LightGBM, XGBoost, SHAP, PuLP MILP) are functional and tested, but currently coupled to synthetic tabular datasets.
* **Readiness for ML Integration:** **YES — 100% READY.** The acquired real Sentinel-2 analytical bands, Copernicus DEM terrain rasters, and 11-year MOIL production records provide a complete, verified foundation to transition the models from synthetic proxies to genuine geospatial and corporate intelligence.
