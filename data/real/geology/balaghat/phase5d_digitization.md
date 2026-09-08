# Phase 5D — Controlled Digitization of Authoritative GSI Geology Report

**Target AOI:** Balaghat Manganese Mine Area of Interest (5 km × 5 km, UTM Zone 44N / EPSG:32644)  
**Spatial Bounds (WGS84):** `min_lon: 80.2039`, `max_lon: 80.2523`, `min_lat: 21.8239`, `max_lat: 21.8689`  
**Anchor Point:** `80.2281° E, 21.8464° N` (`MOIL_BALAGHAT`)  
**Audit Date:** September 2026  
**Status:** Step 1 Verification Complete — Controlled Stop Condition Triggered  

---

## 1. Step 1 Source Verification & Inventory Audit

In accordance with **Step 1 ("Before digitization: List every file under `data/real/geology/balaghat/raw/`. If the actual source map is NOT present, STOP. Do not fabricate or reconstruct it. Report the missing source instead")**, an exhaustive audit of the `raw/` data directory was performed:

* **Inspected Directory:** `data/real/geology/balaghat/raw/`
* **Raw Files Discovered:** **0 files found** (empty directory).
* **Missing Artifacts:** High-resolution georeferenced raster/PDF map sheets for **GSI Balaghat District Resource Map (1:250,000)** and **Survey of India / GSI 1:50,000 Toposheets 64 C/1 & 64 C/5**.
* **Root Cause:** As documented in Phase 5B and 5C, national Indian portals (**NGDR** at `geodataindia.gov.in`, **GSI Bhukosh** at `bhukosh.gsi.gov.in`, and **Survey of India** at `onlinemaps.surveyofindia.gov.in`) mandate interactive user session authentication (Indian mobile OTP / OCBIS credentials) for full-resolution map downloads. Automated CLI scrapers cannot bypass this portal authentication.

---

## 2. Mandatory Stop Condition Triggered

Under the **Critical Stop Conditions** specified for Phase 5D:
> *"STOP and report instead of generating data if: the acquired source file cannot be found; geological contacts cannot be distinguished; source provenance cannot be established. Do not solve uncertainty by guessing."*

**Action Taken:**  
* **ZERO** synthetic geological polygons or lineaments have been generated.
* **ZERO** files from the legacy `scripts/process_geology_balaghat.py` script were copied or executed.
* **ZERO** derived GIS GeoJSON layers (`lithology.geojson`, `structures.geojson`, `mineral_occurrences.geojson`) were created from guesswork or approximations.

---

## 3. Georeferencing Framework & Ground Control Points (GCPs) Ready for Ingestion

When the user provides the raw map PDF/GeoTIFF raster file into `data/real/geology/balaghat/raw/`, the mathematically established GCP control network is ready for immediate affine/polynomial transformation:

| GCP ID | Feature Description | Longitude ($^\circ \text{E}$) | Latitude ($^\circ \text{N}$) | Expected Function |
|---|---|---|---|---|
| **GCP_01** | Seam Graticule Tic (64 C/1 & 64 C/5 South) | `80.250000°` | `21.750000°` | Graticule alignment along eastern AOI boundary |
| **GCP_02** | Seam Graticule Tic (64 C/1 & 64 C/5 North) | `80.250000°` | `22.000000°` | Graticule alignment along eastern AOI boundary |
| **GCP_03** | 64 C/1 Southwest Degree Corner | `80.000000°` | `21.750000°` | Degree sheet quadrant control |
| **GCP_04** | 64 C/5 Southeast Degree Corner | `80.500000°` | `21.750000°` | Degree sheet quadrant control |
| **GCP_VAL** | Surveyed Bharweli Shaft Portal | `80.228100°` | `21.846400°` | Independent topographic ground validation only |

* **Expected Georeferencing RMSE:** $< 15.0 \text{ meters}$ (for 1:50,000 sheets); $\approx 50.0 \text{ meters}$ (for 1:250,000 DRM).

---

## 4. Current Digitized Layers Status & Inventory

| Target GIS Layer | File Path | Status | Count | Provenance Classification |
|---|---|---|---|---|
| **Lithological Units** | `data/derived/geology/balaghat/lithology.geojson` | **Not Generated** | 0 | Blocked until raw map placed in `raw/` |
| **Structural Lineaments** | `data/derived/geology/balaghat/structures.geojson` | **Not Generated** | 0 | Blocked until raw map placed in `raw/` |
| **Mineral Occurrences** | `data/derived/geology/balaghat/mineral_occurrences.geojson` | **Not Generated** | 0 | Blocked until raw map placed in `raw/` |
| **Georeferenced Raster** | `data/derived/geology/balaghat/gsi_64c_georeferenced.tif` | **Not Generated** | 0 | Blocked until raw map placed in `raw/` |

---

## 5. Technical & Pipeline Validation

1. **Python Data Pipeline Tests:**
   * Ran: `.venv\Scripts\python.exe -m pytest -v tests/test_data.py`
   * Result: **8 passed in 0.99s (100% GREEN)**. Existing tests for MOIL mines registry, Sentinel-2 7-band processing, and Copernicus DEM derivatives remain fully validated and intact.
2. **Frontend Production Build:**
   * Ran: `npm run build` in `frontend/`
   * Result: **Vite build successful in 1.97s** (dist artifacts compiled without errors).

---

## 6. Recommended User Action to Complete Digitization

To execute the genuine digitization without synthetic data:
1. **Acquire Raw Sheet:** Download the high-resolution PDF/GeoTIFF for Sheet **64 C/1** (and/or Balaghat DRM) from the [NGDR Portal](https://geodataindia.gov.in) or [Survey of India Portal](https://onlinemaps.surveyofindia.gov.in) via user login.
2. **Deposit Raw File:** Place the file into `g:\Tattvam\TATTVA\data\real\geology\balaghat\raw/` (e.g. `gsi_balaghat_drm_2002.pdf` or `soi_64c1_topo.pdf`).
3. **Trigger Controlled Digitization:** Once the physical file is present in `raw/`, the automated georeferencing and vector tracing pipeline can execute deterministically with full mathematical audit trails.

---

## 7. Final Verdict

# **C. DIGITIZATION BLOCKED BY SOURCE/QUALITY ISSUE**

### Explanation
In strict compliance with the Phase 5D provenance rules, digitization was halted at Step 1 because no raw raster map file is currently stored under `data/real/geology/balaghat/raw/`. Rather than resorting to guesswork or falling back on the synthetic approximations in `process_geology_balaghat.py`, data generation was halted to preserve absolute data integrity in TATTVA.
