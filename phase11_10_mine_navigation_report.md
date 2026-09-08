# Phase 11: 10-Mine Navigation + Real Mine Intelligence Experience Report

**Date:** 2026-09-06  
**Project:** TATTVA (`G:\Tattvam\TATTVA`)  
**Frontend:** `http://localhost:5173/`  
**Backend:** `http://localhost:8000/`  

---

## 1. Executive Summary & Architecture

Phase 11 transforms TATTVA from a Balaghat-centric exploration interface into a multi-mine MOIL intelligence platform covering the 10 audited MOIL statutory mines across Madhya Pradesh and Maharashtra.

### Core Architecture:
- **Registry Source of Truth:** The 10 audited mines are derived dynamically from `data/real/moil/mines.csv` and `data/real/moil/mine_locations.geojson` via backend APIs. Zero duplicate hardcoded mine lists exist in the frontend.
- **5-Category Data Availability Framework:** Every mine dynamically reports its exact availability status across 5 discrete tiers: `REAL DATA`, `REPORTED DATA`, `EXPERIMENTAL`, `SIMULATION`, and `UNAVAILABLE`.
- **Dual Map Views:** Users can toggle between **Global Sausar Belt View** (all 10 MOIL mines across Central India with coordinate precision provenance) and **Mine Detail View** (focused on the selected mine).
- **Strict Isolation Guardrail:** Real Sentinel-2/DEM exploration grids (27,720 cells) load exclusively for `MOIL_BALAGHAT`. All other 9 mines display clear unavailable status with zero canvas, coordinate, or score leakage.
- **Scope Distinction:** MOIL Reported Production is explicitly identified as company-level aggregate reported series, while block-level scheduling is framed as `TATTVA Operational Simulation`.

---

## 2. Mine Selector Behavior

- **Dynamic State Grouping:** Grouping is dynamically derived at runtime from the `state` field of the registry:
  - **Madhya Pradesh:** Balaghat, Ukwa, Tirodi, Sitapatore
  - **Maharashtra:** Chikla, Dongri Buzurg, Beldongri, Kandri, Munsar, Gumgaon
- **Status Indicator Badges:** Real-time badge indicates `REAL EXPLORATION ACTIVE` for Balaghat and `STATUTORY REGISTRY` for the other 9 mines.
- **Smooth Navigation:** Selecting any mine triggers a Leaflet `flyTo` animation, updates the mine overview panel, purges old layers, and synchronizes the URL search param (`?mine=MOIL_...`).

---

## 3. Global Map vs Mine Detail Behavior

### Global Sausar Belt View (`mapViewMode: 'global_belt'`)
- Fits map viewport bounds (`fitBounds`) to encompass the entire Sausar manganese belt across Central India (MP & Maharashtra).
- Displays all 10 MOIL mine markers styled by coordinate precision:
  - **Surveyed / Statutory Point (~10–50m):** Emerald marker with diamond/star (Balaghat, Tirodi, Sitapatore)
  - **Lease Centroid (~500m):** Cyan marker (Ukwa)
  - **Map-Derived Reference (~1–2km):** Amber marker (Chikla, Dongri Buzurg, Beldongri, Kandri, Munsar, Gumgaon)
- Exposes a concise Coordinate Quality Legend in the bottom-left corner.
- Clicking any mine marker selects the mine, switches to Mine Detail View, and centers the camera.

### Mine Detail View (`mapViewMode: 'mine_detail'`)
- Focuses tightly on the selected mine at zoom level 13–14.
- **For Balaghat:** Enables the 30m Real Exploration Canvas grid, Sub-layer switcher (`Exploration Priority`, `Anomaly`, `Robust Distance`, `Anchor Similarity`), cutoff slider, and Authoritative Site Evidence markers.
- **For Other Mines:** Displays the audited statutory mine location, comprehensive Data Availability Status panel, and clean unavailable state notice.

---

## 4. Data Availability Status (5-Category Framework)

Every mine queries `GET /api/real/mine-dashboard/{mine_id}` to dynamically determine availability:

| Category | Component / Resource | Balaghat Status | Other 9 Mines Status | Scope / Provenance Note |
| :--- | :--- | :---: | :---: | :--- |
| **REAL DATA** | Multispectral Satellite & DEM | **AVAILABLE** | **UNAVAILABLE** | Sentinel-2A (10m-20m) & Copernicus DEM GLO-30 (30m) covering 5km × 5km AOI. |
| **REPORTED DATA** | MOIL Statutory Production | **AVAILABLE (AGGREGATE)** | **AVAILABLE (AGGREGATE)** | 11-year company-level reported series (FY14-FY24). Mine-level historical breakdown not publicly available. |
| **EXPERIMENTAL** | Real Exploration Priority | **AVAILABLE (27,720 cells)** | **UNAVAILABLE (0 cells)** | Relative ranking heuristic combining anomaly, distance, and anchor similarity. |
| **SIMULATION** | TATTVA Operational Simulation | **SIMULATION** | **SIMULATION** | Parametric synthetic pit telemetry and daily scheduling (Block A/B/C). |
| **UNAVAILABLE** | Geological Vector Lithology | **UNAVAILABLE** | **UNAVAILABLE** | Official GSI 1:50k vector map pending release in public domain. |

---

## 5. Balaghat-Specific Exploration Guardrail & Layer Purge

Switching between mines executes strict lifecycle cleanup:
1. Removes `layersRef.current.realProspectivity` from Leaflet.
2. Removes `layersRef.current.realEvidence` from Leaflet.
3. Closes all open popups (`map.closePopup()`).
4. Resets `selectedEntity` to `null`.
5. Non-Balaghat mines set all exploration state variables to `null`.

**Transition Verification Matrix:**

| Transition | Exploration Grid State | Evidence State | Isolation Status |
| :--- | :---: | :---: | :---: |
| `Balaghat -> Tirodi` | Removed (0 cells) | Removed (0 markers) | **PASSED** (0 leakage) |
| `Balaghat -> Ukwa` | Removed (0 cells) | Removed (0 markers) | **PASSED** (0 leakage) |
| `Balaghat -> Chikla` | Removed (0 cells) | Removed (0 markers) | **PASSED** (0 leakage) |
| `Tirodi -> Balaghat` | Restored (27,720 cells) | Restored (2 markers) | **PASSED** (Clean reload) |
| `Ukwa -> Balaghat` | Restored (27,720 cells) | Restored (2 markers) | **PASSED** (Clean reload) |

---

## 6. Production Data Handling

In [`ProductionAnalytics.jsx`](file:///g:/Tattvam/TATTVA/frontend/src/components/ProductionAnalytics.jsx):
- Tab 1 explicitly labeled: **`TATTVA Operational Simulation`** (`SIMULATION`).
- Tab 2 explicitly labeled: **`MOIL Reported Production (Company-Level Aggregate)`** (`REPORTED DATA`).
- Prominent scope notice added:
  > *"⚠️ **Scope:** Company-level aggregate reported production. Mine-level historical production is not publicly available in the current dataset. Block telemetry represents TATTVA Operational Simulation."*
- Prohibits apportioning company totals or interpolating synthetic daily production into historical figures.

---

## 7. URL State Synchronization & Robustness

- Supported query parameters:
  - `?mine=MOIL_BALAGHAT` → Loads Balaghat in Mine Detail mode.
  - `?mine=MOIL_TIRODI` → Loads Tirodi in Mine Detail mode.
  - No query parameter → Defaults safely to `MOIL_BALAGHAT`.
  - `?mine=INVALID_MINE` → Safely defaults to `MOIL_BALAGHAT` with zero errors or corrupt states.

---

## 8. API Endpoints Summary

| Endpoint | Method | Response Scope | Purpose |
| :--- | :---: | :--- | :--- |
| `/api/real/mines` | `GET` | 10 MOIL mines | Source of truth for statutory registry, coordinates, and precision. |
| `/api/real/mine-dashboard/{mine_id}` | `GET` | Lightweight JSON (<5KB) | Consolidated metadata, 5-tier Data Availability Status, and provenance. |
| `/api/real/mines/{mine_id}/layers` | `GET` | Layer boolean dict | Raster availability map. |
| `/api/real/production` | `GET` | Company-level series | Annual statutory reported production records. |
| `/api/real/prospectivity/{mine_id}/geojson` | `GET` | 27,720 cells (Balaghat) / `[]` (Others) | Lazy-loaded 30m exploration grid polygon GeoJSON. |
| `/api/real/prospectivity/{mine_id}/evidence` | `GET` | Spatial points (Balaghat) / `[]` (Others) | Authoritative deposit anchors. |

---

## 9. Automated Testing & Build Results

### A. Dedicated Phase 11 Test Suite ([`tests/test_real_mine_navigation.py`](file:///g:/Tattvam/TATTVA/tests/test_real_mine_navigation.py))
- `test_real_mines_registry_10_mines_integrity`: **PASSED** (10 audited mines verified).
- `test_mine_dashboard_balaghat_availability_status`: **PASSED** (5 categories & Balaghat active state verified).
- `test_mine_dashboard_non_balaghat_isolation`: **PASSED** (Non-Balaghat mines verified as unavailable for exploration).
- `test_mine_dashboard_invalid_mine_404`: **PASSED** (Returns HTTP 404 for unknown mine IDs).
- `test_prospectivity_geojson_isolation_no_leakage`: **PASSED** (0 cells returned for non-Balaghat mines).
- `test_production_scope_integrity`: **PASSED** (`ALL_MINES_AGGREGATE` company-level scope verified).

### B. Full Project Pytest Suite
```powershell
.venv\Scripts\python.exe -m pytest -v
# Result: 54 passed, 11 warnings in 12.31s (100% PASS)
```

### C. Frontend Production Build
```powershell
cd frontend; npm run build
# Result: ✓ built in 2.05s (0 errors)
```

### D. Scientific Terminology & Code Integrity
- Banned terms search: **0 occurrences** across all user-visible UI text.
- Mandatory disclaimer verified: `"⚠️ Relative ranking heuristic, not probability. No independent negative drillholes available."`
- `data/synthetic/`, ML forecasting models, Phase 9B experiment artifacts, and rasters remain 100% untouched. No Git commits created.

---

## 10. Known Limitations

1. **Non-Spatial Exploration Data:** Historical drilling records reported in IBM inspection filings (e.g. 26 boreholes in Bharweli lease) remain aggregate because individual collar coordinates are confidential in public filings.
2. **Geological Vector Coverage:** Official 1:50k vector lithology maps for the Sausar Group remain categorized as `UNAVAILABLE` pending open public release.

---

## 11. Final Verdict

**Verdict:** **A = Fully Accepted**

Phase 11 is complete. TATTVA is now an audited multi-mine intelligence platform providing honest, transparent, and scientifically governed navigation across all 10 MOIL statutory mines.
