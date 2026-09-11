# Phase 15: TATTVA Backend Data Foundation & DSR 2022 Integration Report

**Date:** September 2026  
**Project:** TATTVA (MOIL Mining Intelligence Suite)  
**Classification Standard:** Strict 5-Tier Data Governance (`REAL` | `SOURCE-DERIVED` | `DERIVED` | `SIMULATION` | `EXPERIMENTAL`)

---

## 1. Executive Summary

Phase 15 integrates genuine statutory mining, geological, leasehold, grade, exploration, production, and constraint data from the **Balaghat District Survey Report (DSR 2022)** and associated authoritative records (Indian Bureau of Mines MCDR mining plans, MoEFCC PARIVESH clearances, Geological Survey of India Memoirs) directly into TATTVA's backend foundation.

This phase is **Backend & Data First**:
- Establishes the dedicated `data/real/dsr/balaghat/` source namespace.
- Preserves the existing Phase 14C minimalist industrial UI without redesign.
- Augments the authoritative 10-mine MOIL registry with multi-point coordinate classifications (`point_type`).
- Implements mathematical verification for lease boundary polygons and surveyed boundary pillars without artificial geometry distortion.
- Enforces strict isolation between macro reported production, district aggregates, approved mine-plan targets, and micro operational simulations.
- Validates 109 automated tests (all 85 baseline tests + 24 new backend foundation tests passing).

---

## 2. Integrated DSR 2022 Datasets (`data/real/dsr/balaghat/`)

| Dataset File | Dataset Name | Records | Data Status | Provenance Status | Primary Authority |
|---|---|---|---|---|---|
| `source_manifest.json` | Balaghat DSR Source Manifest | 4 Sources / 11 Datasets | `source-derived` | `verified` | Directorate of Geology and Mining MP |
| `README.md` | DSR Data Dictionary & Governance | — | `source-derived` | `verified` | DGM MP & IBM |
| `mine_registry.csv` | Balaghat District Mine & Leasehold Registry | 6 Mining Leases | `source-derived` | `verified` | Balaghat DSR 2022 & IBM |
| `lease_areas.csv` | Lease Area & Clearance Breakdown | 6 Leases | `source-derived` | `verified` | DSR 2022 & MoEFCC PARIVESH |
| `boundary_pillars.csv` | Surveyed Lease Boundary Pillars | 24 Boundary Pillars | `source-derived` | `verified` | IBM MCDR Mining Plans |
| `boundaries.geojson` | Validated Lease Boundaries & Pillars | 2 Polygons / 2 Points | `source-derived` | `verified` | IBM MCDR & Survey Records |
| `geology_reference.csv` | Sausar Group Stratigraphy & Ore Beds | 7 Formations | `source-derived` | `verified` | GSI Bulletin 22 & DSR 2022 |
| `grade_reference.csv` | Grade & Chemical Assay Distributions | 8 Grade Classes | `source-derived` | `verified` | MOIL Specs & DSR 2022 |
| `exploration_evidence.csv` | Exploration Boreholes & UNFC Reserves | 5 Prospects/Leases | `source-derived` | `verified` | IBM MCDR & GSI Inventory |
| `production_reference.csv` | District & Mine Reported Production | 14 Annual Records | `source-derived` | `verified` | Balaghat DSR 2022 & IBM |
| `mine_plan_targets.csv` | Approved Mine Plan & EC Production Targets | 8 Plan Records | `source-derived` | `verified` | IBM Approved Mining Plans |
| `constraints.csv` | Mining & Operational Constraints | 9 Parameters | `source-derived` | `verified` | DGMS, MoEFCC & IBM |

---

## 3. Audited Existing Datasets & Reclassification

All existing datasets were re-audited under the 5-tier classification framework:

1. **`data/real/moil/mines.csv` & `mine_locations.geojson` (`REAL`)**:
   - Augmented with `point_type` (`shaft_portal`, `lease_centroid`, `mine_site_reference`), `tehsil`, and `lease_area_ha`.
   - Backward compatibility preserved for all 10 statutory MOIL mines.
2. **`data/real/geology/balaghat/mineralization_evidence.csv` (`SOURCE-DERIVED`)**:
   - Contains 14 regional mineral occurrences and shaft coordinates from GSI Bulletin 22 and MoEFCC filings.
   - Retained as regional positive exploration anchors.
3. **`data/synthetic/` (`SIMULATION`)**:
   - `production_daily.csv`, `equipment_events.csv`, `drillhole_assay.csv`, `mine_blocks.geojson`, and `satellite_features_grid.csv` remain strictly classified as `SIMULATION`.
   - None were deleted; they are necessary for software demonstration and ML sandbox modeling where proprietary shift logs and 3D collar databases are unreleased.

---

## 4. Boundary Geometry Handling & Area Verification

Boundary pillars from statutory mining plans were compiled and validated for planar polygon closure and area calculation:

### A. Bharweli Underground/Opencast Lease (`MOIL_BALAGHAT`)
- **Reported Lease Area:** $180.44\text{ Ha}$
- **Calculated Planar Area (UTM 44N Shoelace):** $181.03\text{ Ha}$
- **Discrepancy:** $+0.33\%$ (well within standard geodetic cartographic survey tolerance)
- **Geometry Status:** `reconstructed_polygon_verified` (10 surveyed perimeter pillars, closed ring).

### B. Ukwa Leasehold (`MOIL_UKWA`)
- **Reported Core Lease Area:** $199.07\text{ Ha}$
- **Total Consolidated Leasehold (with extension):** $247.63\text{ Ha}$
- **Calculated Planar Area:** $243.75\text{ Ha}$
- **Discrepancy:** $-1.57\%$ vs consolidated perimeter
- **Geometry Status:** `reconstructed_polygon_verified` (10 surveyed perimeter pillars).

### C. Tirodi & Sitapatore Leases (`MOIL_TIRODI`, `MOIL_SITAPATORE`)
- **Geometry Status:** `point_only_pillars_unclosed`
- Discontiguous multi-hill opencast pit geometries (West + East Tirodi) are preserved as discrete surveyed reference pillars and statutory centroids rather than fabricating unclosed polygons.

---

## 5. Geological & Grade Handling

- **Textual Geology vs GIS Polygons:** Sausar Group stratigraphic units (Bichua, Junewani, Chorbaoli, Mansar, Lohangi, Sitasaongi, Tirodi Gneiss) are structured as reference data in `geology_reference.csv`. Textual formation descriptions are **not** converted into arbitrary cell polygons without official 1:50k vector cadastre.
- **Statistical Grade Reference vs Drillhole Collars:** Chemical assay intervals (% Mn, % Fe, % SiO2, % P) from DSR Table 3.4 and MOIL commercial grade sheets are stored as statistical distributions in `grade_reference.csv`. Individual synthetic drillhole collars (BH001, etc.) were **not** manufactured from aggregate statistics.

---

## 6. Exploration & Production Scope Governance

TATTVA strictly separates four distinct production and exploration data tiers:

```
┌───────────────────────────────────────────────────────────────────────────┐
│                          PRODUCTION SCOPE SEPARATION                      │
├────────────────────────────────┬──────────────────────────────────────────┤
│ Scope Tier                     │ Representation & Dataset                 │
├────────────────────────────────┼──────────────────────────────────────────┤
│ 1. MOIL Company Reported       │ Audited 11-year corporate annual series  │
│                                │ (data/real/moil/production/)             │
│ 2. District Reported           │ Balaghat district annual totals (DSR)    │
│                                │ (data/real/dsr/balaghat/production_ref)  │
│ 3. Mine-Level Reported         │ Statutory mine actuals (IBM/DSR)         │
│                                │ (data/real/dsr/balaghat/production_ref)  │
│ 4. Mine-Level Planned          │ Approved 5-Year mining plan targets (DSR)│
│                                │ (data/real/dsr/balaghat/mine_plan_tgts)  │
│ 5. Operational Simulation      │ Parametric 3-block daily shift logs      │
│                                │ (data/synthetic/production_daily.csv)    │
└────────────────────────────────┴──────────────────────────────────────────┘
```

- Planned production is **never** converted into actual production.
- Corporate production is **never** allocated down to individual mines without explicit statutory source tables.

---

## 7. Machine Learning Impact Assessment

1. **Exploration Priority Baseline:**
   - The Phase 9B exploration model (Tree-Isolation Anomaly + PCA-Decorrelated Robust Mahalanobis + Bharweli Anchor Similarity) remains the **authoritative baseline**.
   - DSR 2022 provides textual stratigraphy and aggregate drillhole counts; because these do not provide cell-level spatial contact vectors across the entire $5\times 5\text{ km}$ AOI, the baseline ML model is **preserved without blind mutation**.
   - No synthetic negative exploration labels were manufactured.
2. **Production Forecasting & Optimization:**
   - LightGBM probabilistic forecaster remains calibrated against the operational simulation benchmark.
   - PuLP MILP optimizer constraints are augmented with DSR-derived recovery rates ($82.5\%$), sand stowing ratios ($1.15\text{ m}^3/\text{t}$), and environmental caps ($8.0\text{ Lakh Tonnes/yr}$).

---

## 8. Backend API Endpoints Added

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/api/real/dsr` | Balaghat DSR 2022 source manifest & dataset inventory | `200` |
| `GET` | `/api/real/dsr/mines` | Source-derived Balaghat mine & lease registry | `200` |
| `GET` | `/api/real/dsr/{mine_id}` | Consolidated DSR profile for a specific mine | `200` / `404` |
| `GET` | `/api/real/dsr/{mine_id}/boundaries` | Validated boundary polygon GeoJSON & surveyed pillars | `200` / `404` |
| `GET` | `/api/real/dsr/{mine_id}/geology` | Sausar Group stratigraphy and ore bed associations | `200` / `404` |
| `GET` | `/api/real/dsr/{mine_id}/grade` | Chemical grade ranges and commercial fractions | `200` / `404` |
| `GET` | `/api/real/dsr/{mine_id}/exploration` | Aggregate borehole counts, meterage, and UNFC reserves | `200` / `404` |
| `GET` | `/api/real/dsr/{mine_id}/production` | Reported historical actuals vs approved plan targets | `200` / `404` |
| `GET` | `/api/real/dsr/{mine_id}/constraints` | Mining, environmental, and operational constraints | `200` / `404` |

---

## 9. Final Data Inventory Table

| Module | Dataset | Status | Source | Used By | Provenance Status | Remaining Gap |
|---|---|---|---|---|---|---|
| **Mine Registry** | `data/real/moil/mines.csv` | `REAL` | IBM, MoEFCC, SOI | Loader, API, Map | `verified` | None |
| **DSR Mine Registry** | `data/real/dsr/balaghat/mine_registry.csv` | `SOURCE-DERIVED` | Balaghat DSR 2022 | Loader, `/api/real/dsr/mines` | `verified` | Private sub-leases unlocated |
| **Lease Boundaries** | `data/real/dsr/balaghat/boundaries.geojson` | `SOURCE-DERIVED` | DSR 2022 & IBM MCDR | Loader, API, Map | `verified` | Unclosed pits remain points |
| **Boundary Pillars** | `data/real/dsr/balaghat/boundary_pillars.csv` | `SOURCE-DERIVED` | IBM Mining Plans | Loader, `/api/real/dsr/*/boundaries` | `verified` | Intermediate pillars in forest |
| **Geology Reference** | `data/real/dsr/balaghat/geology_reference.csv` | `SOURCE-DERIVED` | GSI Bulletin 22, DSR | Loader, `/api/real/dsr/*/geology` | `verified` | Vector lithology map pending |
| **Grade Reference** | `data/real/dsr/balaghat/grade_reference.csv` | `SOURCE-DERIVED` | MOIL Product Specs, DSR | Loader, `/api/real/dsr/*/grade` | `verified` | Micro block-level assays |
| **Exploration Evidence**| `data/real/dsr/balaghat/exploration_evidence.csv` | `SOURCE-DERIVED` | IBM MCDR, MECL | Loader, `/api/real/dsr/*/exploration`| `verified` | Proprietary collar database |
| **Drillhole Assays** | `data/synthetic/drillhole_assay.csv` | `SIMULATION` | 3D Gaussian random field | Geostatistics (IDW Grade) | `simulation` | Full collar DB confidential |
| **Satellite Imagery** | `data/real/sentinel2/balaghat/raw/` | `REAL` | ESA Copernicus Sentinel-2A | Raster extraction, Grid | `verified` | None |
| **DEM** | `data/real/dem/balaghat/raw/` | `REAL` | Copernicus GLO-30 DEM | Terrain extraction, Grid | `verified` | None |
| **Reported Production**| `data/real/moil/production/production_reported.csv` | `REAL` | MOIL Statutory Annual Reports | Production API, Reconciliation | `verified` | None |
| **DSR Production** | `data/real/dsr/balaghat/production_reference.csv` | `SOURCE-DERIVED` | Balaghat DSR 2022 | Loader, `/api/real/dsr/*/production` | `verified` | Monthly mine granularity |
| **Mine Plan Targets** | `data/real/dsr/balaghat/mine_plan_targets.csv` | `SOURCE-DERIVED` | IBM Approved Mining Plans | Loader, `/api/real/dsr/*/production` | `verified` | Annual revisions |
| **Operational Constraints**| `data/real/dsr/balaghat/constraints.csv` | `SOURCE-DERIVED` | DGMS, IBM, MoEFCC | Optimization, `/api/real/dsr/*/constraints` | `verified` | Real-time sensor limits |
| **Equipment Telemetry**| `data/synthetic/equipment_events.csv` | `SIMULATION` | Semi-Markov failure process | SHAP Root-Cause Attribution | `simulation` | Live SCADA telemetry |
| **Daily Production** | `data/synthetic/production_daily.csv` | `SIMULATION` | Gaussian-Markov simulation | LightGBM Forecaster | `simulation` | Live weighbridge SCADA |
| **Exploration ML** | `data/derived/geospatial/balaghat/prospectivity_experiment.csv` | `EXPERIMENTAL` | Isolation Forest + Mahalanobis | `/api/real/prospectivity/*` | `derived_from_real` | Ground truth negative assays |
| **Optimization Model** | PuLP Constrained MILP | `EXPERIMENTAL` | Real Constraints + Sim State | Scenario Dispatch Engine | `derived` | Proprietary fleet dispatch |

---

## 10. Verification Results

1. **Python Automated Test Suite:**
   ```bash
   .venv\Scripts\python.exe -m pytest -v
   ====================== 109 passed, 55 warnings in 29.47s ======================
   ```
   - 85 existing unit/integration tests: **PASSED**
   - 24 new Phase 15 DSR backend foundation tests: **PASSED**
   - Regressions: **0**

2. **Frontend Build Verification:**
   ```bash
   cd frontend && npm run build
   ✓ 2437 modules transformed.
   ✓ built in 14.29s (dist/ compiled cleanly with 0 errors)
   ```
