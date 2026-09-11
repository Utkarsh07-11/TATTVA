# PHASE 16 — DATA UTILIZATION & FEATURE IMPACT AUDIT
**TATTVA Geospatial Mining Intelligence Platform**  
**Date:** September 11, 2026  
**Status:** COMPLETE & AUDITED  
**Repository:** `G:\Tattvam\TATTVA`  

---

## 1. Executive Summary

Phase 16 executes a comprehensive **Data Utilization and Feature Impact Audit** on the TATTVA platform following the data provenance and lease geometry corrections completed in Phase 15.1. 

The primary objective of this phase is to evaluate how the newly integrated **SOURCE-DERIVED** Balaghat District Survey Report (DSR 2022) datasets can be safely, defensibly, and traceably utilized across TATTVA's decision modules **WITHOUT** fabricating spatial, temporal, assay, production, telemetry, or drillhole data.

### Core Audit Principles & Findings
1. **Absolute Data Provenance Rule Enforced**: No textual geology descriptions, aggregate regional exploration counts, or annual company-wide totals are converted into fabricated drillholes, artificial polygons, or synthetic daily sensor logs.
2. **Strict 7-Tier Provenance Taxonomy**: Every data artifact is classified into one of: `REAL / SURVEYED`, `SOURCE-DERIVED`, `SOURCE-DERIVED / PARTIAL`, `DERIVED`, `REFERENCE`, `SIMULATION`, or `UNAVAILABLE`.
3. **Preservation of ML Integrity**: DSR tabular stratigraphy, regional grade spans, and aggregate borehole counts **are NOT injected into ML feature vectors** (e.g., Phase 9B 30m prospectivity grid or LightGBM production forecaster) due to spatial scale mismatch, temporal discontinuity, and target leakage risks. All existing ML algorithms (LightGBM Quantile Forecaster, Tree-SHAP, Isolation Forest, PCA-decorrelated Mahalanobis, Bharweli Anchor Similarity, and PuLP MILP) remain strictly unchanged and untampered with.
4. **Targeted Decision & Context Integration**: High-value DSR records have been integrated into narrowly scoped REST endpoints (`/api/real/dsr/{mine_id}/context`, `/evidence`, `/production`, `/constraints`) providing authoritative administrative, stratigraphical, mineral reserve, and statutory constraint context for Resource Explorer, Scenario Sandbox, and Mine Reconciliation views.
5. **Zero Regression Verification**: The complete test suite of **117 automated tests passed (100%)** with zero errors, and the frontend production build compiled cleanly in **2.13s with 0 errors**.

---

## 2. Phase 16 Governance Rules (Rules 6–10)

To ensure long-term architectural integrity and eliminate any possibility of data conflation, five mandatory governance rules have been formalized and verified in the automated test suite:

### Rule 6: Source-Scope Preservation
- **Principle**: Every DSR record must strictly retain its original scope and semantic meaning.
- **Enforcement**:
  - District aggregate figures, company-level reported production (`MOIL_COMPANY_ANNUAL_REPORTED`), and mine-specific reported actuals (`MINE_ANNUAL_REPORTED`) are maintained in isolated data structures.
  - Mine-specific planned targets (`PLANNED / TARGET`) from approved mining plans are isolated from historical actuals.
  - Source-reported reserve/resource classifications (UNFC 111 / 121 / 122), engineering constraints, and operational daily simulations (`SIMULATION`) are never silently converted into one another.

### Rule 7: No Implied Spatialization
- **Principle**: A textual or aggregate DSR record must NOT be assigned to the 30m feature grid merely because it refers to Balaghat, Bharweli, Ukwa, or another mine.
- **Enforcement**:
  - Spatial linkage requires defensible coordinates, verified boundary geometry, or documented spatial coverage.
  - Textual stratigraphy in `geology_reference.csv` and aggregate counts in `exploration_evidence.csv` are served as non-spatial reference metadata (`spatial_status: "NON_SPATIAL_REGIONAL_REFERENCE"`, `geometry_status: "UNAVAILABLE"`).
  - No synthetic raster pixels or fake polygon masks are generated from narrative descriptions.

### Rule 8: No Implied Temporalization
- **Principle**: Annual, plan-period, or historical reference values must NOT be converted into daily, shift, monthly, or timestamped observations.
- **Enforcement**:
  - Financial year fields (e.g., `"2021-22"`) are preserved as macro period labels.
  - No synthetic daily interpolation, spline fitting, or shift allocations are performed on annual or 5-year plan targets.
  - Operational time-series engines remain strictly isolated from DSR annual reference records.

### Rule 9: Reserve / Resource Governance
- **Principle**: UNFC (United Nations Framework Classification) and other source-reported resource/reserve figures remain source-reported classifications.
- **Enforcement**:
  - TATTVA surfaces UNFC G1/G2/G3 metrics strictly with a mandatory evidentiary disclaimer: *"Documented statutory exploration evidence from Balaghat DSR 2022. Not independently estimated or ML-predicted reserves."*
  - The platform does NOT present UNFC figures as current mineable inventory or algorithmic predictions.

### Rule 10: Constraint Governance
- **Principle**: An engineering or environmental constraint may only enter an optimization/scenario calculation when its numerical value, unit, scope, applicable mine/activity, and provenance are explicitly available in the source-derived dataset.
- **Enforcement**:
  - Only explicitly quantified parameters with unambiguous units (e.g., recovery factor $85.0\%$, stowing ratio $1.15\,\text{m}^3/\text{t}$, dewatering limit $250.0\,\text{m}^3/\text{hr}$, EC ceiling $450,000\,\text{TPA}$) are ingested by the PuLP optimizer or scenario cards.
  - Qualitative or unquantified notes remain documented reference metadata and do not enter mathematical optimization models.

---

## 3. Phase 16A — Data Consumption Matrix

Every source-derived DSR dataset was audited across its full architectural pipeline: from physical CSV/GeoJSON storage to data loaders, validator schemas, REST API endpoints, decision modules, and UI presentation.

| # | Dataset & Path | Provenance Classification | Spatial Grain / Resolution | Temporal Grain | Scope | Current Consumer | Potential Consumer | Safe to Integrate? | Architectural Trace & Status | Risk of Misleading Interpretation |
|---|----------------|---------------------------|----------------------------|----------------|-------|------------------|--------------------|--------------------|------------------------------|-----------------------------------|
| 1 | `mine_registry.csv` | `SOURCE-DERIVED` | Point (Shaft Portal, Site Ref, Centroid) | Static (2022) | 10 Statutory Mines | `DataLoader`, `real_data.py`, `/api/real/mines` | Multi-mine navigation, GIS map overlays | **YES** | Loader $\rightarrow$ Validator $\rightarrow$ API $\rightarrow$ Frontend Mine Selector | Low: Coordinates must clearly indicate point type (`shaft_portal` vs `lease_centroid`) |
| 2 | `lease_areas.csv` | `SOURCE-DERIVED / PARTIAL` | Multi-Lease Table / Administrative | Historical & Current (1962–2022) | Balaghat District Mines | `DataLoader`, `/api/real/dsr/{mine_id}/context` | Legal audit, Resource Explorer context card | **YES** | Loader $\rightarrow$ Validator $\rightarrow$ Context API $\rightarrow$ Details Card | Low: Conflicting values (e.g., Ukwa 199.07 vs 247.63 Ha) clearly documented with grant context |
| 3 | `boundary_pillars.csv` | `REAL / SURVEYED` & `SOURCE-DERIVED` | Point ($X, Y$ UTM / WGS84) | Statutory Gazette / DSR | Pillar Locations (P1..P10, Portal) | `DataLoader`, `validator.py`, `/api/real/dsr/{mine_id}/boundaries` | Map view, surveyor coordinate inspection | **YES** | Loader $\rightarrow$ Boundaries API $\rightarrow$ Leaflet Point Layers | Low: Explicit point types prevent treating single pillars as polygons |
| 4 | `boundaries.geojson` | `UNAVAILABLE` (Polygon) / `SOURCE-DERIVED` (Points) | Point Features (0 closed cadastre polygons) | Static (2022) | Balaghat Tenements | `DataLoader`, `/api/real/dsr/{mine_id}/boundaries` | 2D/3D Map Viewer | **PARTIAL** (Points only) | Loader $\rightarrow$ GeoJSON API $\rightarrow$ Map Viewer (Points rendered, polygon marked Unavailable) | High if polygon is faked; mitigated by removing hand-drawn approximations |
| 5 | `geology_reference.csv` | `SOURCE-DERIVED` | Formation / Lithological Unit (Regional) | Static (Sausar Group Stratigraphy) | Balaghat Manganese Belt | `DataLoader`, `/api/real/dsr/{mine_id}/context` | Resource Explorer Context Panel | **YES** (Textual / Reference only) | Loader $\rightarrow$ Context API $\rightarrow$ Geology Reference Card | High if converted to raster polygons; mitigated by keeping as textual stratigraphy |
| 6 | `grade_reference.csv` | `SOURCE-DERIVED` | Mine-level statistical range / distribution | Static (DSR 2022 / IBM) | Mine-wise Ore Spans | `DataLoader`, `/api/real/dsr/{mine_id}/context` | Resource Explorer Benchmark Card | **YES** (Context only) | Loader $\rightarrow$ Context API $\rightarrow$ Grade Reference Card | Critical if assigned to synthetic collars; mitigated by remaining macro benchmarks |
| 7 | `exploration_evidence.csv` | `SOURCE-DERIVED` | Deposit / Mine Aggregate Counts | Cumulative to 2022 | Boreholes & UNFC Reserves | `DataLoader`, `/api/real/dsr/{mine_id}/evidence` | Exploration Evidence Summary Card | **YES** (Aggregate only) | Loader $\rightarrow$ Evidence API $\rightarrow$ Exploration Card | High if split into fake collar coords; mitigated by showing as regional totals |
| 8 | `production_reference.csv` | `SOURCE-DERIVED` | Mine / Company / District Annual Totals | Annual (FY18 to FY22) | Reported Production | `DataLoader`, `real_data.py`, Reconciliation Engine | Production Intelligence, Benchmark Panel | **YES** (Scope-separated) | Loader $\rightarrow$ Production API $\rightarrow$ Macro Intelligence Panel | High if treated as daily shift sensor data; mitigated by macro scope tagging |
| 9 | `mine_plan_targets.csv` | `SOURCE-DERIVED` | Mine-level Annual Production Targets | Planned Horizon (FY22–FY26) | Statutory EC Approved Caps | `DataLoader`, `/api/real/dsr/{mine_id}/constraints` | Scenario Sandbox, Planning Target Baseline | **YES** (Target only) | Loader $\rightarrow$ Constraints API $\rightarrow$ Scenario Target Input | Critical if confused with actual output; labeled strictly as `PLANNED / TARGET` |
| 10 | `constraints.csv` | `SOURCE-DERIVED` | Mine Operational & Environmental Limits | Statutory Horizon (Current) | Dewatering, Recovery, EC Caps | `DataLoader`, `/api/real/dsr/{mine_id}/constraints` | Optimization Bounds, Scenario Warnings | **YES** (Documented units only) | Loader $\rightarrow$ Constraints API $\rightarrow$ Constraint Checklist | Low: Units explicitly preserved (e.g., $m^3/hr$, $\%$, $t/month$, $m^3/t$) |

---

## 4. Phase 16B — Safe Integration Opportunities

### 1. Resource Explorer (Contextual Evidence)
- **Integration**: Exposed structured lithological units (`geology_reference.csv`), stratigraphic sequences (Mansar Formation, Sitasaongi Formation, Tirodi Gneiss), and grade distributions via `GET /api/real/dsr/{mine_id}/context`.
- **Distinction**: Displayed alongside Sentinel-2 Band Ratios and DEM indices as **Documented Geological Context**, without converting narrative regional geology into artificial cadastral vector polygons.
- **Provenance Tag**: `SOURCE-DERIVED / PARTIAL`.

### 2. Exploration Evidence Module
- **Integration**: Integrated documented cumulative exploratory borehole counts, total core drilling meterage, and UNFC resource classification breakdowns (G1/G2/G3/G4) via `GET /api/real/dsr/{mine_id}/evidence`.
- **Distinction**: Presented strictly as **Authoritative Regional Evidence**. No individual synthetic collar coordinates or simulated downhole assay intervals are fabricated from aggregate counts.

### 3. Mine Registry & Coordinate Reference Points
- **Integration**: Surfaced surveyed and statutory points with strict coordinate typing:
  - `shaft_portal`: Physical portal/shaft location (e.g., Bharweli Holmes Shaft $21.8732^\circ\text{N}, 80.2215^\circ\text{E}$).
  - `mine_site_reference`: Statutory mine office / industrial centroid.
  - `lease_centroid`: Centroid derived from registered grant descriptions.
  - `boundary_pillar`: Surveyed boundary markers ($P_1, P_2, \dots, P_{10}$).
- **Geometry Safeguard**: Polygon geometry remains tagged `UNAVAILABLE` until verified KML/Shapefile DGPS boundary cadastre is officially supplied.

### 4. Production Intelligence (Scope Isolation)
- **Integration**: Actual reported historical production numbers from IBM / DSR 2022 are surfaced through `/api/real/dsr/{mine_id}/production`.
- **Distinction**: Macro reported figures (annual tonnages) are strictly separated from micro simulated operational telemetry. MOIL company-wide figures (1.1–1.3 MTPA) are never partitioned into unverified mine-specific shares without explicit source documentation.

### 5. Reconciliation & Scenario Sandbox
- **Integration**: Approved statutory mine plan capacities from `mine_plan_targets.csv` (e.g., Bharweli 450,000 TPA, Ukwa 150,000 TPA) are exposed as baseline benchmark targets.
- **Labeling**: Displayed unambiguously as **"Source-Derived Statutory Target (EC Approved)"**. They are never merged or conflated with actual production logs.

### 6. Optimization Layer Constraints
- **Integration**: Operational boundaries from `constraints.csv` are passed into the Scenario & Optimization engine:
  - Ore recovery factors: $82.5\% - 85.0\%$.
  - Hydraulic stowing ratio: $1.15\,\text{m}^3/\text{tonne}$.
  - Dewatering discharge limit: $250\,\text{m}^3/\text{hr}$.
  - Environmental Clearance (EC) ceiling caps.
- **Safeguard**: Units and constraints are strictly parsed without inventing missing numerical parameters.

---

## 5. Datasets Intentionally NOT Integrated into Core ML

| Dataset | Rejected Consumer | Technical Rationale & Provenance Risk |
|---------|-------------------|---------------------------------------|
| `geology_reference.csv` | 30m Prospectivity Grid Features | Textual formations (Mansar, Sitasaongi) lack parcel-level spatial GIS boundaries. Rasterizing text descriptions into a 30m grid introduces false spatial precision. |
| `grade_reference.csv` | Drillhole Collar Assay ML Input | General mine-level grade ranges ($30\% - 48\%\,\text{Mn}$) cannot be attributed to specific $X, Y, Z$ depth intervals without actual lab assay logs. |
| `exploration_evidence.csv` | Spatial Anomaly Density Feature | Cumulative borehole counts (e.g., Bharweli 84 holes) lack individual spatial coordinates. Converting counts into point densities would create synthetic spatial clustering artifacts. |
| `mine_plan_targets.csv` | Production Forecasting Training Feature | Planned targets represent administrative ceilings, not actual operational realizations. Using targets as training features creates severe target leakage. |
| `boundaries.geojson` (Approximations) | Training Mask / Polygon Crop | Hand-drawn 10-vertex approximations lack cadastral DGPS backing. Using them as spatial clip masks would distort geospatial raster extractions. |

---

## 6. Phase 16C — ML Feature Impact Audit

### Current Machine Learning Architecture
1. **Prospectivity Ensemble (Phase 9B)**:
   - **Model 1**: Isolation Forest (Contamination $= 0.05$).
   - **Model 2**: PCA-decorrelated Robust Mahalanobis Distance.
   - **Model 3**: Bharweli Mineralization Anchor Cosine Similarity ($k\text{-NN}$).
   - **Inputs**: 30m multi-spectral Sentinel-2 indices (NDVI, Iron Oxide Ratio, Ferrous Iron Ratio, Clay Alteration Ratio) + SRTM DEM derivatives (Elevation, Slope, Aspect, Topographic Position Index).
2. **Production Forecaster**:
   - LightGBM Quantile Regressor ($p10, p50, p90$).
   - Tree-SHAP Feature Attribution.
3. **Operational Optimizer**:
   - PuLP Mixed-Integer Linear Programming (MILP) solver.

### 5-Criteria Feature Usability Evaluation

```
[DSR Candidate Feature] ──► 1. Defensible Spatial Linkage?  ──NO──► REJECT FROM ML (Keep Contextual)
                                   │ YES
                            2. Genuinely Observed/Measured?  ──NO──► REJECT FROM ML (Keep Contextual)
                                   │ YES
                            3. Appropriate Spatial Resolution?──NO──► REJECT FROM ML (Keep Contextual)
                                   │ YES
                            4. Transparent Missingness Handling?──NO─► REJECT FROM ML
                                   │ YES
                            5. Zero Leakage / Scope Conflation? ──NO─► REJECT FROM ML
                                   │ YES
                            ACCEPT AS ML FEATURE (Requires Formal Phase)
```

### Usability Evaluation Results

| Candidate DSR Feature | Spatial Linkage (1) | Genuinely Observed (2) | Resolution Match (3) | Missingness (4) | Zero Leakage (5) | Final Decision |
|-----------------------|---------------------|------------------------|----------------------|-----------------|------------------|----------------|
| Regional Lithology Code | ❌ (Deposit scale) | ⚠️ (Textual reference) | ❌ ($>5\,\text{km}$ vs $30\,\text{m}$) | ❌ | ⚠️ | **REJECTED**: Contextual Reference Only |
| Mine Average Mn Grade | ❌ (No collar $XYZ$) | ⚠️ (Quoted range) | ❌ (Mine-wide aggregate) | ❌ | ❌ | **REJECTED**: Contextual Reference Only |
| Cumulative Borehole Count | ❌ (No collar coords) | ✅ (DSR Table) | ❌ (Single scalar per mine) | ❌ | ⚠️ | **REJECTED**: Exploration Evidence Only |
| EC Approved Plan Target | ❌ (Administrative) | ✅ (Statutory filing) | ❌ (Annual mine target) | ❌ | ❌ (Target leakage) | **REJECTED**: Scenario Benchmark Only |
| Pumping Discharge Limit | ❌ (Point facility) | ✅ (Statutory constraint) | ❌ (Non-spatial parameter) | ❌ | ✅ | **REJECTED from ML / ACCEPTED in PuLP MILP** |

---

## 7. Phase 16D — API Audit & Endpoint Specifications

Four specialized REST API endpoints have been implemented and verified in `src/api/routes/real_data.py`:

### 1. `GET /api/real/dsr/{mine_id}/context`
- **Purpose**: Returns authoritative stratigraphy, formation details, grade distribution, and verified lease grant records.
- **Response Schema**:
  ```json
  {
    "mine_id": "bharweli",
    "mine_name": "Balaghat (Bharweli) Mine",
    "data_classification": "SOURCE-DERIVED / PARTIAL",
    "source": "Balaghat District Survey Report (DSR 2022) & IBM MP/MS Records",
    "spatial_status": "POINT_COORDINATES_ONLY",
    "geometry_status": "POLYGON_UNAVAILABLE",
    "geology": { ... },
    "grade_distribution": { ... },
    "lease_records": [ ... ]
  }
  ```

### 2. `GET /api/real/dsr/{mine_id}/evidence`
- **Purpose**: Returns documented exploration summary metrics (borehole counts, drilling meters, UNFC reserves) without collar fabrication.
- **Response Schema**:
  ```json
  {
    "mine_id": "ukwa",
    "data_classification": "SOURCE-DERIVED",
    "source": "Balaghat DSR 2022 Table 4.x / MOIL Exploration Summary",
    "exploration_evidence": {
      "reported_borehole_count": 42,
      "reported_core_meterage_m": 4850.0,
      "unfc_reserves_mt": { "g1_proved": 4.12, "g2_probable": 2.85 },
      "evidence_classification": "DOCUMENTED_REGIONAL_EXPLORATION_RECORD"
    }
  }
  ```

### 3. `GET /api/real/dsr/{mine_id}/production`
- **Purpose**: Exposes reported historical annual production figures tagged with explicit macro scope.
- **Response Schema**:
  ```json
  {
    "mine_id": "bharweli",
    "data_classification": "SOURCE-DERIVED",
    "production_history": [
      { "fiscal_year": "2021-22", "reported_production_tonnes": 420000, "scope": "MINE_ANNUAL_REPORTED" }
    ]
  }
  ```

### 4. `GET /api/real/dsr/{mine_id}/constraints`
- **Purpose**: Delivers statutory mine plan targets, recovery ratios, stowing rates, and dewatering limits for optimization and scenario simulation.
- **Response Schema**:
  ```json
  {
    "mine_id": "bharweli",
    "data_classification": "SOURCE-DERIVED",
    "statutory_plan_target_tpa": 450000,
    "recovery_factor_pct": 85.0,
    "stowing_ratio_m3_per_t": 1.15,
    "dewatering_limit_m3_hr": 250.0
  }
  ```

---

## 8. Phase 16E — Frontend Consumption Audit

The frontend displays source-derived DSR intelligence via **Progressive Disclosure** without cluttering or altering the established cinematic/industrial design theme:

1. **Badge Hierarchy**:
   - `REAL / SURVEYED`: Green border, high confidence badge.
   - `SOURCE-DERIVED`: Blue border, document source reference tag.
   - `SIMULATION`: Purple border, clear synthetic indicator.
   - `UNAVAILABLE`: Muted gray tag, explicitly disclosing missing geometry.
2. **Context Modals & Side Panels**:
   - Drilldown cards display full source citation (e.g., *"Source: Balaghat DSR 2022 Table 3.2, IBM Concession Registry"*).
   - Conflicting values (e.g., Ukwa Lease Area) show explanatory dropdowns with grant historical context.
3. **Map Rendering Integrity**:
   - Points are rendered with distinct SVG icons matching their point types (`shaft_portal`, `lease_centroid`, `boundary_pillar`).
   - Leases lacking surveyed boundary polygons display: *"Surveyed boundary cadastre pending statutory DGPS release."*

---

## 9. Phase 16F — End-to-End Data Lineage Table

```
+-----------------------------+     +--------------------------+     +------------------------------+     +----------------------------+
|  Primary Statutory Source   | ──► | Physical CSV / GeoJSON   | ──► | FastAPI Loader & Validator   | ──► | UI Presentation & Engine   |
| (DSR 2022 / IBM / MOIL AR)  |     | (data/real/dsr/balaghat) |     | (src/data/ + src/api/routes) |     | (Resource Explorer, Cards) |
+-----------------------------+     +--------------------------+     +------------------------------+     +----------------------------+
```

| Field / Metric | Raw Source File | Loader Function | Validator Method | API Endpoint | Frontend / Decision Consumer |
|----------------|-----------------|-----------------|------------------|--------------|------------------------------|
| **Mine Coordinates** | `mine_registry.csv` | `DataLoader.load_mine_registry()` | `DataValidator.validate_mine_registry()` | `GET /api/real/mines` | Multi-Mine Selector & Map Points |
| **Lease Area & Concession** | `lease_areas.csv` | `DataLoader.load_lease_areas()` | `DataValidator.validate_lease_areas()` | `GET /api/real/dsr/{mine_id}/context` | Legal & Cadastral Reference Card |
| **Boundary Pillar Points** | `boundary_pillars.csv` | `DataLoader.load_boundary_pillars()` | `DataValidator.validate_boundary_pillars()` | `GET /api/real/dsr/{mine_id}/boundaries` | Map Survey Pillar Overlays |
| **Stratigraphic Sequence** | `geology_reference.csv` | `DataLoader.load_geology_reference()` | `DataValidator.validate_geology_reference()` | `GET /api/real/dsr/{mine_id}/context` | Regional Stratigraphy Card |
| **Grade Distribution Spans** | `grade_reference.csv` | `DataLoader.load_grade_reference()` | `DataValidator.validate_grade_reference()` | `GET /api/real/dsr/{mine_id}/context` | Grade Benchmark Card |
| **Borehole & Reserve Totals** | `exploration_evidence.csv` | `DataLoader.load_exploration_evidence()` | `DataValidator.validate_exploration_evidence()` | `GET /api/real/dsr/{mine_id}/evidence` | Exploration Evidence Panel |
| **Reported Historical Output** | `production_reference.csv`| `DataLoader.load_production_reference()` | `DataValidator.validate_production_reference()` | `GET /api/real/dsr/{mine_id}/production` | Macro Intelligence View |
| **Approved Plan Targets** | `mine_plan_targets.csv` | `DataLoader.load_mine_plan_targets()` | `DataValidator.validate_mine_plan_targets()` | `GET /api/real/dsr/{mine_id}/constraints` | Scenario Baseline Target |
| **Operational Limits** | `constraints.csv` | `DataLoader.load_constraints()` | `DataValidator.validate_constraints()` | `GET /api/real/dsr/{mine_id}/constraints` | Scenario Sandbox / PuLP Bounds |

---

## 10. Phase 16G — Test Suite & Regression Verification

### 1. Test Suite Summary
- **Total Backend Tests Executed**: 117
- **Passed**: 117 (100%)
- **Failed / Errored**: 0
- **Execution Time**: ~30s

```
====================== 117 passed, 57 warnings in 31.42s ======================
```

### 2. Verified Test Coverage Modules
- `tests/test_dsr_backend_foundation.py` (32 tests):
  - DSR schema loading, coordinate typing, unavailable geometry validation, context & evidence endpoints, 404 handlers.
  - **Governance Rules 6–10 Verification**: Source-scope preservation, no implied spatialization, no implied temporalization, UNFC reserve governance, and constraint governance.
- `tests/test_phase13_integrity.py`: Geospatial CRS integrity, feature grid raster alignment, 10-mine isolation, Tree-SHAP feature attribution, PuLP solver feasibility, reproducibility.
- `tests/test_production_reconciliation.py`: Canonical reported production immutability, zero mine-wise allocation from MOIL totals, reconciliation variance arithmetic, scenario determinism.
- `tests/test_real_mine_navigation.py`: Multi-mine navigation isolation, non-Balaghat prospectivity shielding, production scope tagging.
- `tests/test_real_prospectivity_api.py` & `test_real_prospectivity_experiment.py`: Feature preprocessing, finite model inputs, anomaly monotonicity, anchor similarity, zero synthetic dependency.

### 3. Frontend Production Build Verification
- **Command**: `npm run build`
- **Output**:
  ```
  ✓ 2437 modules transformed.
  ✓ built in 2.13s
  dist/index.html                   0.84 kB
  dist/assets/index-CvHX2g2T.css   47.89 kB
  dist/assets/index-qYhTUC56.js 10,442.34 kB
  ```
- **Result**: Zero TypeScript/JSX compilation errors.

---

## 11. Provenance Risks & Mitigations

| # | Provenance Risk | Potential Failure Mode | Implemented Mitigation & Safeguard |
|---|-----------------|------------------------|------------------------------------|
| 1 | **Boundary Polygon Fabrication** | Drawing rough polygons between known pillars or around centroids creates false cadastre. | All lease geometries lacking verified DGPS vertex loops are explicitly tagged `UNAVAILABLE`. Hand-drawn approximations are deleted. |
| 2 | **Drillhole Assay Synthesis** | Splitting DSR borehole counts into synthetic collar locations with fake grade logs. | DSR exploration data is strictly retained as aggregate deposit evidence records (`reported_borehole_count`, `unfc_reserves_mt`). |
| 3 | **Macro-to-Micro Production Leakage** | Dividing MOIL company annual production (~1.2 MTPA) across 10 mines using synthetic ratios. | Macro production is tagged `MOIL_COMPANY_ANNUAL_REPORTED` and never partitioned into unverified mine-level series. |
| 4 | **Target vs Actual Conflation** | Treating statutory mine plan targets as historical production. | Mine plan numbers are explicitly tagged `PLANNED / TARGET` and restricted to planning/scenario cards. |
| 5 | **Geology Rasterization Leakage** | Rasterizing regional text formations into 30m ML features. | Textual stratigraphy is restricted to context endpoints and explicitly excluded from ML training grids. |

---

## 12. Remaining Data Gaps

1. **Statutory DGPS Cadastral Polygons**: Official boundary pillar closed-loop polygons for Bharweli, Ukwa, and Tirodi remain pending official release by the MP State Mining Department / IBM.
2. **Standardized Downhole Assay Database**: Real-world downhole interval assays ($XYZ$ collar, lithology, $\% \text{Mn}, \% \text{Fe}, \% \text{SiO}_2, \% \text{P}$) are proprietary MOIL assets and remain unavailable for public ML ingestion.
3. **Real-time SCADA Sensor Telemetry**: Mine underground ventilation, dewatering flowmeters, and hoist cycle telemetry remain simulated (`SIMULATION`) in the Digital Mine module.

---

## 13. Recommended Next Phase

### Recommended Phase: **Phase 17 — Production Scenario & Operational Constraint Solver Integration**
- **Objective**: Formally wire the newly exposed `SOURCE-DERIVED` operational constraints (recovery factors, stowing ratios, dewatering limits, and statutory plan targets) into the interactive Scenario Sandbox UI.
- **Scope**:
  1. Add UI parameter controls for statutory constraints in the Reconciliation & Scenario Sandbox view.
  2. Implement real-time violation warnings when user-adjusted scenario targets exceed statutory EC caps.
  3. Keep ML models and spatial rasters fully isolated while providing deep operational decision support.

---

**AUDIT CONCLUSION**: Phase 16 is successfully finalized. All SOURCE-DERIVED Balaghat DSR 2022 datasets have been audited, classified, and safely integrated into contextual, evidentiary, and constraint decision layers without fabricating any spatial, temporal, assay, or telemetry observations.
