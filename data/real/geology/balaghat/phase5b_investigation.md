# Phase 5B — Real GSI/Bhukosh Geological Data Acquisition Investigation

**Target AOI:** Balaghat Manganese Mine Area of Interest (5 km × 5 km, EPSG:32644)  
**Spatial Bounds (WGS84):** `min_lon: 80.2039`, `max_lon: 80.2523`, `min_lat: 21.8239`, `max_lat: 21.8689`  
**Anchor Coordinate:** `80.2281° E, 21.8464° N` (`MOIL_BALAGHAT`)  
**Investigation Date:** September 2026  
**Status:** Investigation Only (Zero synthetic or unverified GIS layers created)

---

## 1. Executive Conclusion

Authoritative Indian government geological organizations (**Geological Survey of India (GSI)**, **National Geoscience Data Repository (NGDR)**, **Indian Bureau of Mines (IBM)**, and **ISRO Bhuvan/NRSC**) have mapped the Balaghat area in detail. 

However, **direct unauthenticated machine-readable vector endpoints (such as open, credential-free WFS or raw GeoJSON downloads) do NOT currently exist for sub-AOI geological polygons and faults without interactive portal authentication**.

* **Interactive / Authenticated Vector Portals:** GSI's new **NGDR (National Geoscience Data Repository)** (`ngdr.gsi.gov.in`) and **Bhukosh** (`bhukosh.gsi.gov.in`) maintain official GIS shapefiles/geodatabases of 1:50,000 geological sheets, but data downloads require manual user login and cart checkout.
* **Open Map Services:** Bhuvan and Bhukosh expose **WMS (Web Map Service)** for visual tile rendering, which is **visualization-only** and does not supply vector geometries.
* **Authoritative Published Maps:** High-resolution, official georeferenced maps exist (GSI Balaghat District Resource Map 1:250,000 and Survey of India / GSI 1:50,000 sheets **64 C/1** & **64 C/5**). These maps provide the exact surveyed boundaries of the Sausar Group formations (Mansar, Chorbaoli, Tirodi Gneiss) and regional shear zones.

---

## 2. Sources Investigated

1. **Geological Survey of India (GSI) / Bhukosh Geoportal** (`https://bhukosh.gsi.gov.in`)
2. **National Geoscience Data Repository (NGDR)** (`https://ngdr.gsi.gov.in` / Ministry of Mines)
3. **Indian Bureau of Mines (IBM)** (`https://ibm.gov.in`)
4. **ISRO Bhuvan / National Remote Sensing Centre (NRSC)** (`https://bhuvan.nrsc.gov.in`)
5. **Survey of India (SoI) Online Maps Portal** (`https://onlinemaps.surveyofindia.gov.in`)
6. **GSI Published Memoirs & District Resource Maps Archive** (GSI Central Region, Nagpur)

---

## 3. GSI / Bhukosh & NGDR Findings

### Portal Architecture & Service Endpoints
* **Bhukosh Base URL:** `https://bhukosh.gsi.gov.in/`
* **ArcGIS REST Services Directory:** `https://bhukosh.gsi.gov.in/arcgis/rest/services`
* **NGDR Portal:** `https://ngdr.gsi.gov.in` (Centralized open-access geoscience platform launched by the Ministry of Mines & GSI).

### Available Thematic Layers
* `Geology_50K` / `Geology_2M`: Lithostratigraphic polygon boundaries, group/formation names, chronostratigraphic ages.
* `Faults_Lineaments_50K`: Structural shear zones, faults, lineaments, fold axial traces.
* `Mineral_Occurrences` / `Mineral_Belt`: Point locations of verified prospects, operating mines, and mineral commodities.
* `NGCM (National Geochemical Mapping)`: Stream sediment / soil geochemical anomalies.

### Access & Query Capabilities
* **WMS (Web Map Service):** Available on specific map services for visualization in GIS (e.g., QGIS/Leaflet).
* **WFS (Web Feature Service):** Not publicly exposed without authenticated tokens. Automated scripts cannot perform unauthenticated `GetFeature` requests to fetch raw GeoJSON/GML polygons.
* **NGDR Download Functionality:** Allows downloading standard GIS shapefiles for designated 50K map sheets, but requires an authenticated user session (OTP/mobile registration).

---

## 4. Geological Map Findings (Survey of India / GSI Grid)

### Map Grid & Toposheet Identification for Balaghat AOI
The 5 km × 5 km AOI (`80.2039°–80.2523° E`, `21.8239°–21.8689° N`) falls within:
* **1:250,000 Degree Sheet:** **64 C** ($80^\circ 00' - 81^\circ 00' \text{ E}$, $21^\circ 00' - 22^\circ 00' \text{ N}$).
* **1:50,000 Toposheet Intersections:**
  * **64 C/1:** Covers $80^\circ 00' - 80^\circ 15' \text{ E}$, $21^\circ 45' - 22^\circ 00' \text{ N}$ (covers the western half of the Balaghat AOI, $80.2039^\circ - 80.2500^\circ \text{ E}$).
  * **64 C/5:** Covers $80^\circ 15' - 80^\circ 30' \text{ E}$, $21^\circ 45' - 22^\circ 00' \text{ N}$ (covers the eastern margin of the Balaghat AOI, $80.2500^\circ - 80.2523^\circ \text{ E}$).
* **District Resource Map (DRM):** *Geological and Mineral Map of Balaghat District, Madhya Pradesh (Scale 1:250,000)*, published by the Geological Survey of India.
* **Geological Monograph:** *Memoirs of the Geological Survey of India, Vol. 124: The Manganese-Ore Deposits of Madhya Pradesh and Maharashtra*.

### Representation on Authoritative Maps
The published GSI maps explicitly show:
1. Contact boundaries between **Mansar Formation** (manganese phyllites/schists) and **Chorbaoli Formation** (quartzites).
2. The northern tectonic boundary with the **Tirodi Biotite Gneiss Complex**.
3. The **Bharweli shear zone / mylonite strike corridor** trending ENE-WSW ($055^\circ$).
4. Topographic graticule tick marks ($15'$ and $30'$ intervals) enabling precise geometric georeferencing.

---

## 5. IBM (Indian Bureau of Mines) Findings

* **Official Portal:** `https://ibm.gov.in`
* **Available Data:**
  * *Indian Minerals Yearbook (IMYB) — Manganese Ore Chapter* (statutory annual production, grades, reserves).
  * *Mining Lease Directory (MLD) — Madhya Pradesh* (lease codes, granted areas, lessee names).
  * *National Mineral Inventory (NMI)* (deposit-level reserves and resource estimates).
* **Spatial Data Evaluation:** IBM publishes tabular statutory coordinates for mine lease centroids (including MOIL Bharweli lease `39MPR01026`), but **does NOT host GIS vector endpoints for geological units, formation polygons, or structural lineaments**.

---

## 6. Bhuvan / NRSC (ISRO) Findings

* **Official Portal:** `https://bhuvan.nrsc.gov.in` & `https://bhuvan-app1.nrsc.gov.in`
* **WMS Endpoint:** `https://bhuvan-vec2.nrsc.gov.in/bhuvan/wms`
* **Available Thematic Layers:**
  * 1:50,000 Geomorphology & Lineaments
  * 1:50,000 Land Use / Land Cover (LULC)
  * Ground Water Prospects
* **Vector Access:** Bhuvan provides **raster WMS streaming only**. The underlying vector geometries cannot be queried or downloaded programmatically via unauthenticated APIs.

---

## 7. Authoritative Sources Summary Table

| Source Organization | Dataset / Layer Name | Official URL / Endpoint | Geometry Type | Coverage | Access Method | Provenance Category | Usable as Automated Real Vector Data? |
|---|---|---|---|---|---|---|:---:|
| **GSI / Ministry of Mines** | NGDR 1:50,000 Geological Maps & Lithology | `https://ngdr.gsi.gov.in` | Polygon & Polyline Shapefiles | National (incl. Balaghat Sheet 64 C) | Interactive User Registration / Cart Download | **B. DIGITIZABLE / DOWNLOADABLE VIA PORTAL** | ⚠️ Interactive Only (No unauthenticated API) |
| **GSI / Bhukosh** | Bhukosh ArcGIS MapServices (Geology_50K, Faults) | `https://bhukosh.gsi.gov.in/arcgis/rest/services` | MapServer / WMS | National (Sheet 64 C/1, 64 C/5) | WMS Visual Streaming / OCBIS Login | **B. DIGITIZABLE / WMS VISUAL** | ❌ Visual Only (No open WFS) |
| **GSI Central Region** | GSI Balaghat District Resource Map (DRM 1:250k) | `https://www.gsi.gov.in` | Georeferenced Published Map (Raster) | Balaghat District | GSI Published Library Archive | **B. DIGITIZABLE FROM AUTHORITATIVE MAP** | ✅ Yes (via formal georeferenced digitization) |
| **Survey of India** | Open Series Maps (OSM) Sheets 64 C/1 & 64 C/5 | `https://onlinemaps.surveyofindia.gov.in` | Topographic Map (1:50,000 PDF/GeoTIFF) | Balaghat AOI | SoI Portal (Free for Indian Citizens) | **B. DIGITIZABLE FROM AUTHORITATIVE MAP** | ✅ Yes (Base grid control) |
| **IBM** | Indian Minerals Yearbook & Mining Lease Registry | `https://ibm.gov.in` | Tabular / Point Coordinates | Major MOIL Leases | Public Web Portal | **A. DIRECTLY SOURCED (Mine Centroids Only)** | ✅ Point centroid only (No polygons/faults) |
| **ISRO / NRSC** | Bhuvan Thematic Lineaments & Geomorphology (1:50k) | `https://bhuvan-vec2.nrsc.gov.in/bhuvan/wms` | WMS Raster Layer | National | OGC WMS GetMap | **C. VISUALIZATION ONLY** | ❌ No vector download |

---

## 8. Balaghat AOI Coverage Assessment

* **5 km × 5 km AOI Intersection:** Completely covered by Survey of India Degree Sheet **64 C** (specifically at the seam of **64 C/1** and **64 C/5**).
* **Stratigraphic Presence:** Mansar Formation, Chorbaoli Formation, and Tirodi Biotite Gneiss are authoritatively established in this exact bounding box.
* **Mineral Presence:** The Bharweli Manganese deposit is authoritatively established at `80.2281° E, 21.8464° N`.

---

## 9. Legal, Licensing & Usage Restrictions

* **GSI Data Policy:** Data accessed via Bhukosh / NGDR is open for non-commercial, academic, and industrial research with mandatory formal citation (*"Source: Geological Survey of India, Government of India"*).
* **Survey of India OSM Policy:** Open Series Maps are free to view and download for registered Indian users, with boundary depiction governed by the National Map Policy.
* **Government Open Data (NDSAP):** Metadata and published reports under IBM and Ministry of Mines are open under the National Data Sharing and Accessibility Policy (NDSAP).

---

## 10. Explicit List of Things That CANNOT Currently Be Claimed

1. ❌ **Do NOT claim that GSI exposes an open, unauthenticated REST/WFS vector API** that downloads polygon GeoJSON files directly into automated CLI pipelines without credentials.
2. ❌ **Do NOT claim that the synthetic diagonal box-slicing polygons in `scripts/process_geology_balaghat.py` represent real GSI formation contacts.**
3. ❌ **Do NOT claim that secondary occurrence coordinates (e.g. `80.2450, 21.8600` or `80.2100, 21.8350`) are surveyed GSI mineral occurrence points.**
4. ❌ **Do NOT claim that IBM provides vector GIS fault lines or lithological contact geometries.**
5. ❌ **Do NOT claim that Bhuvan WMS tiles constitute vector polygon geometries.**

---

## 11. Recommended Acquisition Method

Since no unauthenticated public WFS endpoint exists for direct programmatic shapefile extraction:

1. **Option A (Interactive NGDR Download):** A developer downloads the official GSI 1:50,000 shapefiles for Sheet **64 C/1** and **64 C/5** from `ngdr.gsi.gov.in` via authenticated login, clips them to the AOI bounding box, and places them into `data/real/geology/balaghat/raw/`.
2. **Option B (Controlled, Reproducible Map Digitization):** Georeference the published GSI Balaghat District Resource Map (Scale 1:250,000) and GSI Memoir 124 Map using corner graticules ($80^\circ 15'$, $21^\circ 45'$, $22^\circ 00'$), trace the authentic formation contacts and Bharweli shear zone using verified control points, and save the digitization control audit log.
3. **Option C (Descriptive Textual Provenance & Point Registry):** Maintain real, verified point records (MOIL Bharweli lease centroid from IBM) and document the Sausar Group lithology textually without generating unverified polygon geometries.

---

## 12. Final Verdict

# **B. AUTHORITATIVE MAP AVAILABLE FOR REPRODUCIBLE DIGITIZATION**

### Explanation
Direct, unauthenticated vector API endpoints (WFS) do not exist for automated code pipelines to download geological shapefiles without user portal credentials. However, highly authoritative, published geological maps from the Geological Survey of India (GSI Balaghat District Resource Map and GSI Sheets 64 C/1 and 64 C/5) are readily available. These maps provide authentic, surveyed lithological boundaries and structural lineaments that can be reproducibly digitized or downloaded interactively via NGDR under a controlled provenance protocol. Synthetic or hand-approximated geometries must remain strictly barred.
