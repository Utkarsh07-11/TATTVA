# Phase 15: TATTVA Backend Data Audit & Provenance Inventory

**Date:** September 2026  
**Project:** TATTVA (MOIL Mining Intelligence Platform)  
**Scope:** Complete repository dataset audit covering Real, Source-Derived, Derived, Synthetic/Simulation, and Processed data layers.

---

## 1. Data Classification Standard

TATTVA strictly enforces a 5-tier classification hierarchy:

| Tier | Name | Definition |
|---|---|---|
| **1** | **REAL** | Directly reported or officially published by an authoritative statutory agency (e.g. MOIL Statutory Disclosures, ESA Copernicus L2A, Copernicus GLO-30 DEM, IBM). |
| **2** | **SOURCE-DERIVED** | Extracted and structured from authentic government reports, mining plans, geological memoirs, or district survey publications (e.g. Balaghat DSR 2022, GSI Memoir Series A No. 22). When original PDFs are preserved in archive but pending full re-audit, classified as `SOURCE-DERIVED / PROVENANCE PARTIAL`. |
| **3** | **DERIVED** | Deterministically calculated via mathematical or geospatial transformations (e.g. NDVI, slope, aspect, hillshade, YoY growth) from Real or Source-Derived data. |
| **4** | **SIMULATION** | Artificially generated operational telemetry, block dispatch logs, or synthetic assays used for software demonstration and decision-support sandboxing when actual proprietary data is unavailable. |
| **5** | **EXPERIMENTAL** | Machine learning rankings, anomaly scores, relative exploration heuristics, and scenario optimization outputs. |

---

## 2. Comprehensive Dataset Inventory & Audit Table

| Dataset | Current Classification | Source | Coverage | Used By | Provenance Completeness | Action |
|---|---|---|---|---|---|---|
| `data/real/moil/mines.csv` | **REAL** | IBM MCDR, MoEFCC PARIVESH, SOI Toposheets | 10 MOIL Operating Mines (MP & Maharashtra) | `src/data/loader.py`, `/api/real/mines`, frontend map | **Verified** (Audited statutory records) | **AUGMENT** (Add `point_type`, tehsil, Khasra, lease area from DSR) |
| `data/real/moil/mine_locations.geojson` | **REAL** | IBM, MoEFCC PARIVESH, SOI | 10 MOIL Mines | `src/data/loader.py`, `/api/real/mines`, frontend map | **Verified** (Audited coordinate points) | **AUGMENT** (Add `point_type` attributes) |
| `data/real/moil/production/production_reported.csv` | **REAL** | MOIL Annual Reports, IBM Indian Minerals Yearbook | MOIL Corporate & State Totals (FY14–FY24) | `src/data/loader.py`, `/api/real/production`, Reconciliation | **Verified** (Statutory audited reports) | **KEEP** (Authoritative macro production) |
| `data/real/sentinel2/balaghat/raw/*.tif` | **REAL** | ESA Copernicus Sentinel-2A L2A (2024-04-17) | Balaghat AOI (5 km x 5 km) | Raster extraction, Feature Grid | **Verified** (ESA Level-2A BOA) | **KEEP** (Authoritative surface reflectance) |
| `data/real/dem/balaghat/raw/copernicus_dem_30m_balaghat.tif` | **REAL** | ESA / Airbus WorldDEM GLO-30 | Balaghat AOI (5 km x 5 km) | DEM extraction, Feature Grid | **Verified** (ESA GLO-30 1 arc-sec) | **KEEP** (Authoritative elevation model) |
| `data/real/geology/balaghat/mineralization_evidence.csv` | **SOURCE-DERIVED** | GSI Bulletin 22, MoEFCC EC, IBM MCDR | Balaghat District (14 regional sites) | `src/data/loader.py`, `/api/real/prospectivity/MOIL_BALAGHAT/evidence` | **Verified** (Primary citations audited) | **KEEP** (Regional mineralization anchors) |
| `data/derived/sentinel2/balaghat/*.tif` | **DERIVED** | Deterministic band math on Sentinel-2 | Balaghat AOI (5 km x 5 km) | Feature grid, Map overlays | **Verified** (Deterministic equations) | **KEEP** (NDVI, NDWI, band ratios) |
| `data/derived/dem/balaghat/*.tif` | **DERIVED** | Horn algorithm on Copernicus DEM | Balaghat AOI (5 km x 5 km) | Feature grid, Map overlays | **Verified** (Deterministic equations) | **KEEP** (Slope, aspect, hillshade) |
| `data/derived/production/moil_annual_yoy_growth.csv` | **DERIVED** | Percentage formula on reported production | MOIL Corporate (10 years) | Analytics engine | **Verified** (Deterministic YoY math) | **KEEP** (Annual growth rates) |
| `data/derived/geospatial/balaghat/real_feature_grid.csv` | **DERIVED** | Regular 30m sampling of Real/Derived rasters | Balaghat AOI (27,720 cells) | Phase 9B Prospectivity Model | **Verified** (Rasterio extraction) | **KEEP** (ML feature matrix) |
| `data/derived/geospatial/balaghat/prospectivity_experiment.csv` | **EXPERIMENTAL** | Isolation Forest + Mahalanobis + Anchor Sim | Balaghat AOI (27,720 cells) | `/api/real/prospectivity/MOIL_BALAGHAT/geojson` | **Documented** (Phase 9B experimental pipeline) | **KEEP** (Baseline exploration ranking) |
| `data/synthetic/production_daily.csv` | **SIMULATION** | Parametric Gaussian-Markov simulator | Balaghat Mine (Block A, B, C; 2023–2026) | `DataLoader.load_production_data()`, LightGBM | **Simulation** (Demonstration sandbox) | **LEAVE SIMULATION** (Required for micro forecast) |
| `data/synthetic/equipment_events.csv` | **SIMULATION** | Semi-Markov failure process | Fleet EXC-01..05, DRL-01..03 (2023–2026) | `DataLoader.load_equipment_events()`, Root Cause | **Simulation** (Demonstration sandbox) | **LEAVE SIMULATION** (Required for downtime SHAP) |
| `data/synthetic/drillhole_assay.csv` | **SIMULATION** | 3D Gaussian random field | 100 synthetic collars (Block A, B, C) | `DataLoader.load_drillhole_assay()`, IDW Grade | **Simulation** (Demonstration sandbox) | **LEAVE SIMULATION** (No proprietary drillhole DB) |
| `data/synthetic/satellite_features_grid.csv` | **SIMULATION** | Synthetic 50x50 spatial grid | Synthetic proxy grid | Legacy XGBoost classifier | **Simulation** (Demonstration sandbox) | **LEAVE SIMULATION** (Legacy test compatibility) |
| `data/synthetic/mine_blocks.geojson` | **SIMULATION** | Operational sub-pit layout | Block A, B, C | Frontend map, Mine overview | **Simulation** (Demonstration sandbox) | **LEAVE SIMULATION** (Micro-block boundary) |

---

## 3. DSR 2022 Integration Scope & Action Plan

To ground TATTVA on genuine Balaghat district data, we create the dedicated source namespace `data/real/dsr/balaghat/` containing:

1. `source_manifest.json`: Machine-readable metadata for all DSR 2022 records.
2. `README.md`: Data dictionary, provenance chain, and limitations.
3. `mine_registry.csv`: Balaghat district manganese mines/leases (Bharweli, Ukwa, Tirodi, Sitapatore, Ramrama, Miragpur) with Tehsil, Village, Khasra, Lease Area (Ha), Mining Method, and Status.
4. `lease_areas.csv`: Granular leasehold area breakdowns (forest/non-forest, grant periods, EC approved capacities).
5. `boundary_pillars.csv`: Surveyed boundary pillar coordinates (lat/lon, UTM 44N X/Y, precision, elevation).
6. `geology_reference.csv`: Sausar Group stratigraphic units (Bichua, Junewani, Chorbaoli, Mansar, Lohangi, Sitasaongi, Tirodi Gneiss) and manganese reef characteristics.
7. `grade_reference.csv`: Statistical grade distribution by deposit/formation (Mn %, Fe %, SiO2 %, P %).
8. `exploration_evidence.csv`: Aggregate exploration history (borehole counts, meterage, drilling agencies, UNFC reserves).
9. `production_reference.csv`: District-level and mine-level reported historical production (`reported_actual`, `reported_aggregate`).
10. `mine_plan_targets.csv`: Approved mine-plan production caps (`planned`).
11. `constraints.csv`: Mining, environmental, and optimization constraints (bench height, stripping ratio, stowing, recovery %, dewatering limits).
12. `boundaries.geojson`: Reconstructed lease boundary polygons and pillar feature points.
