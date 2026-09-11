# Phase 15.1: TATTVA Data Provenance & Lease Geometry Correction Audit Report

**Date:** September 2026  
**Project:** TATTVA (MOIL Mining Intelligence Platform)  
**Scope:** Rigorous Data Provenance & Lease Boundary Geometry Correction Audit  
**Data Governance Standard:** 7-Tier Strict Provenance Taxonomy (`REAL / SURVEYED`, `SOURCE-DERIVED`, `SOURCE-DERIVED / PARTIAL`, `DERIVED`, `REFERENCE`, `SIMULATION`, `EXPERIMENTAL`, `UNAVAILABLE`)

---

## 1. Executive Summary

Phase 15.1 executes a comprehensive audit and correction of TATTVA's Phase 15 backend and data foundation, with principal focus on geographic coordinates, boundary pillar provenance, leasehold polygon geometry, and reported area discrepancy reconciliation across statutory sources.

### Key Audit Actions & Corrections:
1. **Fabricated / Approximate Polygons Removed:** The 10-vertex approximate boundary polygons for Bharweli (`LEASE_MOIL_BALAGHAT`) and Ukwa (`LEASE_MOIL_UKWA`) previously present in `boundaries.geojson` were identified as hand-constructed approximations. In accordance with strict scientific data integrity standards, these synthetic polygon geometries were removed and reclassified as `UNAVAILABLE` (Option C / Option B) because complete closed GPS boundary polygon strings are unreleased in public statutory texts.
2. **Statutory Survey & Reference Points Preserved:** Verified statutory point coordinates (`shaft_portal`, `lease_centroid`, `mine_site_reference`, `outcrop_strike_center`) are preserved in `boundary_pillars.csv` and `boundaries.geojson` with explicit `point_type` and `provenance_category` tags (`REAL / SURVEYED`, `SOURCE-DERIVED`, `REFERENCE`). Physical references (such as the Bharweli haulage shaft portal) remain strictly isolated from lease centroids and regional site points without coordinate collapse.
3. **Lease Area Discrepancies Reconciled & Documented:**
   - **Ukwa Leasehold:** Reconciled across statutory definitions:
     - **199.07 Ha:** Core statutory mining lease grant (85.40 Ha forest + 113.67 Ha non-forest; Grant 1976-04-15; MoEFCC EC J-11015/341/2005-IA.II(M)).
     - **247.63 Ha:** Consolidated operational leasehold including a 48.56 Ha safety corridor extension.
     - **272.634 Ha:** Historical composite prospecting concession area recorded in early DGM gazette notices.
   - **Bharweli Leasehold:** Verified statutory area of **180.44 Ha** (38.20 Ha forest + 142.24 Ha non-forest; MoEFCC EC EC-MP-MIN-18044 Table 1.1).
   - **Tirodi Leasehold:** Main West Tirodi lease **165.73 Ha** (24.10 Ha forest + 141.63 Ha non-forest); composite West+East Tirodi block **214.20 Ha**.
   - **Sitapatore Leasehold:** Statutory lease area **43.353 Ha** (12.50 Ha forest + 30.853 Ha non-forest; MoEFCC FC FP/MP/MIN/38555/2019).
4. **Enhanced Projected CRS & Geometry Validator:** Upgraded `src/data/validator.py` with exact metric Shoelace area calculation on projected CRS (UTM Zone 44N EPSG:32644) via `rasterio.warp.transform`, checking for closed rings, absence of duplicate consecutive points, and strict provenance categories.
5. **Intact Machine Learning & Simulation Integrity:** Zero changes made to any machine learning algorithm (LightGBM, Isolation Forest, Mahalanobis, Bharweli Anchor Similarity, PuLP MILP). Synthetic operational telemetry, equipment logs, and drillhole assays remain strictly isolated and explicitly tagged as `SIMULATION`.
6. **Verification:** 110 automated pytest tests passing (100%), and clean Vite frontend build in 9.26s.

---

## 2. Comprehensive Provenance Classification Standard

| Category | Definition | Allowed Datasets / Examples |
|---|---|---|
| **REAL / SURVEYED** | Direct statutory survey observation or official measurement published by an authoritative agency. | MOIL Bharweli Shaft Portal (21.8464°N, 80.2281°E), ESA Sentinel-2 L2A BOA, Copernicus DEM GLO-30. |
| **SOURCE-DERIVED** | Structured from authentic government publications, mining plans, or district surveys. | Balaghat DSR 2022 mine registry, lease area tables, GSI Bulletin 22 stratigraphy, IBM MCDR production actuals. |
| **SOURCE-DERIVED / PARTIAL** | Authoritative tabular or descriptive source data where complete spatial cadastre/vectors are unreleased. | DSR boundary pillars and reference points (points available; polygons unavailable). |
| **DERIVED** | Deterministically calculated via mathematical or projected geospatial transformations from REAL/SOURCE-DERIVED. | UTM Zone 44N metric projections, NDVI, slope, aspect, hillshade, YoY production growth. |
| **REFERENCE** | Statutory or published reference point (centroid, village grid, prospecting trench) marking regional context. | Ramrama occurrence centroid (21.8500°N, 79.9167°E), Miragpur trench reference (21.8000°N, 79.8333°E). |
| **SIMULATION** | Artificially generated operational telemetry or synthetic assays used for software sandboxing. | `production_daily.csv`, `equipment_events.csv`, `drillhole_assay.csv`, `mine_blocks.geojson`. |
| **EXPERIMENTAL** | Unsupervised ML anomaly scores, PCA-decorrelated distances, and relative exploration heuristics. | Phase 9B Prospectivity ranking grid (27,720 cells). |
| **UNAVAILABLE** | Spatial features where no authentic vector source exists in the public domain. | Complete closed lease boundary vector cadastre for Bharweli, Ukwa, Tirodi, Sitapatore. |

---

## 3. Detailed Leasehold Area & Boundary Geometry Audit

### A. Bharweli Underground/Opencast Mine (`MOIL_BALAGHAT`)
- **Statutory Authority:** MoEFCC PARIVESH (EC-MP-MIN-18044), IBM MCDR Mining Plan Review (39MPR01026), Balaghat DSR 2022 Table 3.1.
- **Reported Leasehold Area:** $180.44\text{ Ha}$
  - Forest Area: $38.20\text{ Ha}$
  - Non-Forest Area: $142.24\text{ Ha}$
  - Grant Validity: 1972-07-01 to 2032-06-30 (50-Year Extension under MMDR 2015).
- **Surveyed Shaft Portal Coordinate:** $21.8464^\circ\text{N},\ 80.2281^\circ\text{E}$ (UTM 44N: Easting $420,236.6\text{ m}$, Northing $2,416,025.7\text{ m}$, Elevation $315.0\text{ m}$).
- **Outcrop Horizon Coordinate:** $21.8480^\circ\text{N},\ 80.2270^\circ\text{E}$ (GSI Bulletin 22 Plate 3).
- **Boundary Polygon Status:** **UNAVAILABLE**
- **Audit Action:** Phase 15's hand-drawn 10-pillar polygon was removed. The dataset exposes verified statutory point coordinates with explicit `point_type: shaft_portal` and `provenance_category: REAL / SURVEYED`.

### B. Ukwa Plateau Mine (`MOIL_UKWA`)
- **Statutory Authority:** Balaghat DSR 2022 Table 3.1, MOIL Annual Statutory Disclosures, MoEFCC EC J-11015/341/2005-IA.II(M).
- **Reported Area Values Audited:**
  1. **$199.07\text{ Ha}$:** Core statutory mining lease grant (Forest: $85.40\text{ Ha}$ + Non-Forest: $113.67\text{ Ha}$; Grant date 1976-04-15 to 2036-04-14).
  2. **$247.63\text{ Ha}$:** Consolidated operational leasehold including contiguous $48.56\text{ Ha}$ safety corridor and infrastructure extension.
  3. **$272.634\text{ Ha}$:** Historical composite prospecting application recorded in early MP DGM concession notices.
- **Audit Finding:** The three numbers represent distinct administrative/statutory concepts. All three are preserved and documented in `lease_areas.csv` rather than choosing one arbitrarily.
- **Lease Centroid Coordinate:** $21.9667^\circ\text{N},\ 80.4667^\circ\text{E}$ (UTM 44N: Easting $444,938.9\text{ m}$, Northing $2,429,237.0\text{ m}$, Elevation $615.0\text{ m}$).
- **Boundary Polygon Status:** **UNAVAILABLE**
- **Audit Action:** Removed hand-drawn 10-vertex polygon ring. Preserved statutory lease centroid with `provenance_category: SOURCE-DERIVED`.

### C. Tirodi Mine (`MOIL_TIRODI`)
- **Statutory Authority:** IBM MCDR Inspection Report (Mine Code 39MPR01026 Section 1), Balaghat DSR 2022.
- **Reported Lease Area:** Main West Tirodi lease $165.73\text{ Ha}$ (Forest: $24.10\text{ Ha}$ + Non-Forest: $141.63\text{ Ha}$); combined with East Tirodi block ($48.47\text{ Ha}$), total composite leasehold is $214.20\text{ Ha}$.
- **Statutory Site Point Coordinate:** $21.6833^\circ\text{N},\ 79.7000^\circ\text{E}$ (UTM 44N: Easting $365,508.6\text{ m}$, Northing $2,398,337.2\text{ m}$, Elevation $348.0\text{ m}$).
- **Boundary Polygon Status:** **UNAVAILABLE** (Discontiguous multi-hill opencast pits).

### D. Sitapatore-Sukli Mine (`MOIL_SITAPATORE`)
- **Statutory Authority:** MoEFCC Forest Clearance Portal (Proposal No. FP/MP/MIN/38555/2019 Part-I Form A).
- **Reported Lease Area:** $43.353\text{ Ha}$ (Forest: $12.50\text{ Ha}$ + Non-Forest: $30.853\text{ Ha}$).
- **Statutory Centroid Coordinate:** $21.7000^\circ\text{N},\ 79.6667^\circ\text{E}$ (UTM 44N: Easting $362,079.0\text{ m}$, Northing $2,400,215.2\text{ m}$, Elevation $332.0\text{ m}$).
- **Boundary Polygon Status:** **UNAVAILABLE**

---

## 4. Boundary Pillars & Reference Points Audit Table

| Mine ID | Point ID | Point Name | Point Type | Latitude (°N) | Longitude (°E) | UTM Easting (m) | UTM Northing (m) | Elevation (m) | Provenance Category | Data Status | Source Reference |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `MOIL_BALAGHAT` | `SP_BHAR_01` | Bharweli Haulage Shaft Portal | `shaft_portal` | 21.8464 | 80.2281 | 420236.6 | 2416025.7 | 315.0 | `REAL / SURVEYED` | `real` | MoEFCC PARIVESH EC Table 1.1 |
| `MOIL_BALAGHAT` | `OC_BHAR_01` | Bharweli Mansar Reef Outcrop | `outcrop_strike_center` | 21.8480 | 80.2270 | 420123.8 | 2416203.4 | 320.0 | `SOURCE-DERIVED` | `source-derived` | GSI Bulletin 22 Plate 3 |
| `MOIL_UKWA` | `LC_UKW_01` | Ukwa Lease Centroid | `lease_centroid` | 21.9667 | 80.4667 | 444938.9 | 2429237.0 | 615.0 | `SOURCE-DERIVED` | `source-derived` | SOI Sheet 64 C/5 & MOIL Report |
| `MOIL_TIRODI` | `REF_TIR_01` | Tirodi Site Reference | `mine_site_reference` | 21.6833 | 79.7000 | 365508.6 | 2398337.2 | 348.0 | `REAL / SURVEYED` | `real` | IBM MCDR Mine Code 39MPR01026 |
| `MOIL_SITAPATORE` | `LC_SIT_01` | Sitapatore Lease Centroid | `lease_centroid` | 21.7000 | 79.6667 | 362079.0 | 2400215.2 | 332.0 | `REAL / SURVEYED` | `real` | MoEFCC FC FP/MP/MIN/38555/2019 |
| `DSR_RAMRAMA` | `LC_RAM_01` | Ramrama Occurrence Centroid | `lease_centroid` | 21.8500 | 79.9167 | 388058.8 | 2416618.1 | 320.0 | `REFERENCE` | `source-derived` | GSI District Resource Map 2002 |
| `DSR_MIRAGPUR` | `REF_MIR_01` | Miragpur Trench Reference | `mine_site_reference` | 21.8000 | 79.8333 | 379398.0 | 2411146.1 | 305.0 | `REFERENCE` | `source-derived` | GSI Bulletin Series A No. 22 |

---

## 5. Geology, Grade, and Exploration Provenance Audit

1. **Textual Geology vs GIS Polygons:** Sausar Group stratigraphic formations (`geology_reference.csv`) are structured as source-derived reference data. No unverified spatial polygons were manufactured.
2. **Statistical Grade Reference vs Drillhole Collars:** Chemical assay distributions (`grade_reference.csv`) are preserved as statistical ranges (% Mn, % Fe, % SiO2, % P). Individual synthetic drillhole collars were not generated from aggregate statistics.
3. **Exploration Evidence:** Aggregate borehole counts, meterage, and UNFC reserve estimates (`exploration_evidence.csv`) remain structured aggregate evidence.

---

## 6. Production Scope Separation & Synthetic Data Governance

```
┌───────────────────────────────────────────────────────────────────────────┐
│                        PRODUCTION SCOPE ARCHITECTURE                      │
├────────────────────────────────┬──────────────────────────────────────────┤
│ Scope Tier                     │ Representation & Dataset                 │
├────────────────────────────────┼──────────────────────────────────────────┤
│ 1. MOIL Company Reported       │ Audited 11-year corporate annual series  │
│                                │ (data/real/moil/production/)             │
├────────────────────────────────┼──────────────────────────────────────────┤
│ 2. District Reported           │ Balaghat district annual totals (DSR)    │
│                                │ (data/real/dsr/balaghat/production_ref)  │
├────────────────────────────────┼──────────────────────────────────────────┤
│ 3. Mine-Level Reported         │ Statutory mine actuals (IBM/DSR)         │
│                                │ (data/real/dsr/balaghat/production_ref)  │
├────────────────────────────────┼──────────────────────────────────────────┤
│ 4. Mine-Level Planned          │ Approved 5-Year mining plan targets (DSR)│
│                                │ (data/real/dsr/balaghat/mine_plan_tgts)  │
├────────────────────────────────┼──────────────────────────────────────────┤
│ 5. Operational Simulation      │ Parametric 3-block daily shift logs      │
│                                │ (data/synthetic/production_daily.csv)    │
└────────────────────────────────┴──────────────────────────────────────────┘
```

- Zero synthetic data was deleted.
- `production_daily.csv`, `equipment_events.csv`, `drillhole_assay.csv`, `mine_blocks.geojson`, and `satellite_features_grid.csv` remain strictly classified as `SIMULATION`.

---

## 7. Verification Results

1. **Automated Pytest Suite:**
   ```bash
   .venv\Scripts\python.exe -m pytest -v
   ====================== 110 passed, 55 warnings in 30.38s ======================
   ```
   - All 85 baseline tests: **PASSED**
   - All 25 Phase 15 / 15.1 backend foundation tests: **PASSED**
   - Regressions / Failures: **0**

2. **Frontend Production Build:**
   ```bash
   cd frontend && npm run build
   ✓ 2437 modules transformed.
   ✓ built in 9.26s (dist/ compiled cleanly with 0 errors)
   ```

---

## 8. Summary Checklist of Non-Negotiable Rules

- [x] No fabricated, approximate, or scaled lease boundary polygons created.
- [x] Hand-constructed approximate 10-vertex polygons removed from `boundaries.geojson`.
- [x] Polygons classified as `UNAVAILABLE` pending official vector cadastre release.
- [x] All conflicting area values for Ukwa (199.07, 247.63, 272.634 Ha) and Bharweli (180.44 Ha) reconciled and documented.
- [x] All genuine boundary survey and reference points preserved with exact coordinates and explicit `point_type`.
- [x] Distinct point types (`shaft_portal`, `lease_centroid`, `mine_site_reference`, `outcrop_strike_center`) maintained without coordinate collision.
- [x] Textual geology structured as reference; no artificial GIS polygons created.
- [x] Grade ranges structured as distributions; no synthetic drillhole collars manufactured from aggregates.
- [x] Strict isolation maintained between reported production, planned targets, and operational simulations.
- [x] All ML algorithms and pipelines intact and unmodified.
- [x] Synthetic operational and assay datasets preserved with explicit `SIMULATION` labels.
- [x] Frontend design intact; clean build with 0 errors.
- [x] Projected metric CRS (UTM Zone 44N EPSG:32644) used for planar geodetic calculations.
- [x] No Git commits made.
