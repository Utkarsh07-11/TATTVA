# Phase 9A — Real Mineralization Evidence & Label Audit Report

**Target AOI:** Balaghat Manganese Mine Area of Interest (5 km × 5 km, UTM Zone 44N / EPSG:32644)  
**Spatial Bounds (WGS84):** `min_lon: 80.2039`, `max_lon: 80.2523`, `min_lat: 21.8239`, `max_lat: 21.8689`  
**Anchor Point:** `80.2281° E, 21.8464° N` (`MOIL_BALAGHAT` / Bharweli Shaft)  
**Audit Date:** September 2026  
**Status:** Completed — Strict Provenance Audit & Label Feasibility Assessment  

---

## 1. Executive Summary & Core Findings

1. **Authoritative Evidence Discovered:**
   - **14 Authoritative Mineralization Records** identified and verified across Indian Bureau of Mines (IBM), Geological Survey of India (GSI), Ministry of Mines, MoEFCC PARIVESH, and MOIL statutory filings.
   - **Inside AOI:** 3 records directly inside the 5 km × 5 km Balaghat AOI:
     - `EVID_MOIL_BALAGHAT_BHARWELI_01`: Surveyed Bharweli haulage shaft portal (`80.2281°E, 21.8464°N`, high reliability).
     - `EVID_GSI_BHARWELI_OUTCROP_02`: Mansar Formation manganese reef outcrop strike (`80.2270°E, 21.8480°N`, high reliability).
     - `EVID_IBM_BHARWELI_EXPLORATION_03`: Reported 26 core drillholes (4,850m) in Bharweli lease (non-spatial aggregate disclosure; individual collar GPS coordinates are not public).
   - **Outside AOI (Regional Belt):** 11 records across the Balaghat, Bhandara, and Nagpur manganese belts (Ukwa, Tirodi, Sitapatore, Ramrama, Chikla, Dongri Buzurg, Kandri, Mansar, Gumgaon, Beldongri, Miragpur).

2. **Crucial Absence of Public Exploratory Drillhole Collar Coordinates:**
   - While IBM and MOIL reports confirm that extensive exploratory drilling has occurred in the Balaghat lease (e.g. 26 boreholes, 4,850 metres drilled), **individual borehole collar GPS coordinates and downhole assay interval databases are proprietary lease confidential data and are NOT published in open public PDFs**.
   - No open public database contains coordinates for barren exploratory drillholes.

3. **Zero Synthetic Label Contamination:**
   - In strict compliance with Phase 9A rules, **ZERO synthetic positive or negative labels were generated**.
   - Out of the 27,720 regular 30m grid cells in `real_feature_grid.csv`, exactly:
     - **1 cell** (`GRID-13860`, distance 9.24m) is classified as `positive_candidate` (surveyed portal anchor).
     - **34 cells** (within 100m radius, excluding portal) are classified as `weak_positive_candidate` (active surface pit footprint).
     - **27,685 cells (99.87%)** are strictly classified as `unlabeled`.
   - No cell was assumed to be negative simply because it is not a mine.

---

## 2. Evidence Categorization & Audit Summary

| Evidence ID | Name | Category | Commodity | Coords (WGS84) | Precision | In AOI? | Label Eligibility | Confidence |
|---|---|---|---|---|---|---|---|---|
| `EVID_MOIL_BALAGHAT_BHARWELI_01` | Balaghat (Bharweli) Shaft | Mine / Deposit | Manganese Ore | 21.8464°N, 80.2281°E | Surveyed Point (~10m) | **YES** | `strong_positive_candidate` | **HIGH** |
| `EVID_GSI_BHARWELI_OUTCROP_02` | Bharweli Reef Outcrop | Direct Occurrence | Manganese Ore | 21.8480°N, 80.2270°E | Outcrop Strike (~100m) | **YES** | `strong_positive_candidate` | **HIGH** |
| `EVID_IBM_BHARWELI_EXPLORATION_03`| Bharweli Drilling (26 BH) | Exploration Activity | Manganese Ore | 21.8464°N, 80.2281°E | Non-Spatial Aggregate | **YES** | `context_only` | Low (Non-spatial) |
| `EVID_MOIL_UKWA_04` | Ukwa Mine | Mine / Deposit | Manganese Ore | 21.9667°N, 80.4667°E | Lease Centroid (~500m) | NO (28 km NE) | `weak_positive_candidate` | Medium |
| `EVID_MOIL_TIRODI_05` | Tirodi Mine | Mine / Deposit | Manganese Ore | 21.6833°N, 79.7000°E | Statutory Point (~50m) | NO (58 km SW) | `weak_positive_candidate` | **HIGH** |
| `EVID_MOIL_SITAPATORE_06` | Sitapatore Mine | Mine / Deposit | Manganese Ore | 21.7000°N, 79.6667°E | Lease Centroid (~500m) | NO (62 km SW) | `weak_positive_candidate` | **HIGH** |
| `EVID_GSI_RAMRAMA_07` | Ramrama Occurrence | Direct Occurrence | Manganese Ore | 21.8500°N, 79.9167°E | Village Grid (~1-2km) | NO (32 km W) | `weak_positive_candidate` | Medium |
| `EVID_MOIL_CHIKLA_08` | Chikla Mine | Mine / Deposit | Manganese Ore | 21.5500°N, 79.7500°E | Village Grid (~1-2km) | NO (59 km SW) | `weak_positive_candidate` | Medium |
| `EVID_MOIL_DONGRI_BUZURG_09` | Dongri Buzurg Mine | Mine / Deposit | Manganese Ore | 21.5500°N, 79.6833°E | Village Grid (~1-2km) | NO (65 km SW) | `weak_positive_candidate` | Medium |
| `EVID_MOIL_KANDRI_10` | Kandri Mine | Mine / Deposit | Manganese Ore | 21.4167°N, 79.2667°E | Village Grid (~1-2km) | NO (110 km SW) | `weak_positive_candidate` | Medium |
| `EVID_MOIL_MANSAR_11` | Mansar Mine | Mine / Deposit | Manganese Ore | 21.4000°N, 79.2833°E | Village Grid (~1-2km) | NO (110 km SW) | `weak_positive_candidate` | Medium |
| `EVID_MOIL_GUMGAON_12` | Gumgaon Mine | Mine / Deposit | Manganese Ore | 21.4000°N, 78.9833°E | Village Grid (~1-2km) | NO (138 km SW) | `weak_positive_candidate` | Medium |
| `EVID_MOIL_BELDONGRI_13` | Beldongri Mine | Mine / Deposit | Manganese Ore | 21.4500°N, 79.3000°E | Village Grid (~1-2km) | NO (105 km SW) | `weak_positive_candidate` | Medium |
| `EVID_GSI_MIRAGPUR_14` | Miragpur Occurrence | Direct Occurrence | Manganese Ore | 21.8000°N, 79.8333°E | Village Grid (~1-2km) | NO (41 km WSW) | `weak_positive_candidate` | Medium |

---

## 3. Spatial Relationship Analysis

Descriptive spatial metrics computed against `data/derived/geospatial/balaghat/real_feature_grid.csv` (27,720 cells, 30m spacing):

* **Distance to Audited Balaghat Shaft (`80.2281°E, 21.8464°N`):**
  - Minimum Distance: `9.24 m` (`GRID-13860` at $X=420242.89, Y=2416028.90$)
  - Maximum Distance: `3,504.17 m` (Corner cell `GRID-00001` at $X=417737.89, Y=2418488.90$)
  - Mean Distance: `1,819.53 m`
* **Grid Cell Proximity Counts:**
  - $\le 15\text{ m}$ (Direct shaft cell): **1 cell (0.0036%)**
  - $\le 100\text{ m}$ (Immediate mine pit corridor): **35 cells (0.126%)**
  - $\le 250\text{ m}$ (Near-mine infrastructure buffer): **219 cells (0.790%)**
  - $\le 500\text{ m}$ (Proximal exploration lease envelope): **869 cells (3.135%)**
  - $> 500\text{ m}$ (Regional unevidenced terrain): **26,851 cells (96.865%)**

---

## 4. Assessment of Genuine Negative Labels

* **Investigation Result:** **NO genuine negative labels exist in open public government datasets.**
* **Scientific Rationale:**
  - In mineral exploration, a "negative" label requires physical subsurface testing (e.g. core drilling or trench sampling) that encountered host rock with assay concentrations strictly below economic cutoff grade.
  - The absence of a registered mine at a coordinate does NOT indicate that the subsurface is barren; it merely indicates that no commercial mine portal currently operates at that surface location.
  - Generating synthetic pseudo-negatives from random distant pixels would introduce severe spatial selection bias and invalidate any ML prospectivity model.

---

## 5. Machine Learning Strategy Recommendation

### **Recommended: Strategy B (Positive-Unlabeled Learning) & Strategy D (Unsupervised Anomaly Detection)**

### Why Strategy A (Standard Supervised Classification) is Scientifically UNJUSTIFIED:
* Standard supervised binary classification (e.g., training XGBoost or Random Forest on `Label=1` vs `Label=0`) requires verified positive and verified negative ground truth instances.
* Because the Balaghat AOI contains verified positive spatial anchors (`EVID_MOIL_BALAGHAT_BHARWELI_01`, `EVID_GSI_BHARWELI_OUTCROP_02`) but **0 verified negative drillholes**, assigning arbitrary negative labels to unmined cells would fabricate false geological ground truth.

### Recommended Defensible Methodologies:
1. **Positive-Unlabeled (PU) Learning (Elkan & Noto, 2008; Sansone et al., 2022)**:
   - Treats known mine and outcrop locations as the positive set $P$ and all remaining 27,684 grid cells as the unlabeled background set $U$.
   - Estimates the propensity score $P(s=1|y=1)$ without assuming that unlabeled cells are barren.
2. **Unsupervised Geospatial Anomaly Detection**:
   - Uses Isolation Forests, One-Class SVM, or Mahalanobis spectral distance on the 14 real remote-sensing and terrain features (B02-B12, NDVI, NDWI, band ratios, slope, hillshade) to identify multi-variate anomalies corresponding to distinct lithological or alteration signatures without requiring synthetic labels.

---

## 6. Access & Portal Limitations Documented

1. **National Geoscience Data Repository (NGDR / GSI Bhukosh)**:
   - URL: `https://geodataindia.gov.in`
   - Visible: Interactive WebGIS map viewer displaying Sausar Group regional mineral occurrence points and 1:50k geological map sheet boundaries.
   - Inaccessible via CLI: Direct download of GIS shapefiles/borehole databases requires authenticated Indian mobile SMS OTP login and OCBIS institutional credentials.
2. **IBM MCDR Portal (`https://ibm.gov.in`)**:
   - Visible: Textual inspection PDFs with aggregate borehole counts (e.g. 26 boreholes) and reserve tonnages.
   - Inaccessible: Raw GIS shapefiles and individual borehole collar survey spreadsheets are proprietary lease records not published in public inspection PDF releases.

---

## 7. Phase 9A Final Verdict

# **B. Useful real occurrence evidence exists, but labels are insufficient for conventional supervised learning**

### Justification:
Authoritative government records (IBM, GSI, MoEFCC, MOIL) conclusively establish high-confidence positive spatial anchors for the Bharweli mine portal and manganese reef outcrop in Balaghat. However, because open public records do not provide spatial borehole collar coordinates or verified negative assay points, conventional supervised binary classification is scientifically invalid. Modeling must proceed under **Positive-Unlabeled (PU) Learning** or **Unsupervised Multi-Spectral Anomaly Detection**.
