# Real DEM & Terrain Feature Foundation (Balaghat Mine AOI)

## 1. Overview & Dataset Scope
This dataset establishes the real-world Digital Elevation Model (DEM) and derived physical terrain features for the **MOIL Balaghat Mine** area of interest (Phase 4).

The dataset covers the identical **5 km × 5 km Balaghat AOI** established in Phase 3, anchored on `MOIL_BALAGHAT` (`80.2281° E, 21.8464° N`).

---

## 2. DEM Source Provenance & Investigation

### Candidate Evaluation & Selection
1. **ISRO Bhuvan / NRSC CartoDEM:** Investigated as the primary national Indian DEM candidate. Bhuvan CartoDEM download endpoints (`bhuvan-app1.nrsc.gov.in`) require interactive user authentication via Indian mobile SMS OTP and session-locked Captcha verification, making automated, reproducible pipelines infeasible.
2. **Copernicus DEM (GLO-30):** Selected as the authoritative, unauthenticated, zero-credential public 30 m digital surface model. Produced by the European Space Agency (ESA) in collaboration with Airbus Defence and Space under the Copernicus Programme, referenced to WGS84 and EGM2008 geoid.

### Source Metadata
* **Provider:** European Space Agency (ESA) & Airbus Defence and Space
* **Product Name:** Copernicus Digital Elevation Model GLO-30
* **Tile ID:** `Copernicus_DSM_COG_10_N21_00_E080_00_DEM`
* **Source Registry:** `https://registry.opendata.aws/copernicus-dem/`
* **Download URL:** `https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N21_00_E080_00_DEM/Copernicus_DSM_COG_10_N21_00_E080_00_DEM.tif`
* **Native CRS:** `EPSG:4326` (WGS84)
* **Native Resolution:** 1 arc-second (~30 meters, `0.00027778°`)
* **Vertical Datum & Units:** `EGM2008 Geoid`, meters above sea level
* **Access Method:** Windowed Cloud-Optimized GeoTIFF (COG) HTTP range requests — zero credentials required.

---

## 3. Real Source vs. Derived Terrain Data

### Real Source Data (`data/real/dem/balaghat/raw/`)
* **`copernicus_dem_30m_balaghat.tif`:** Unmodified 1 arc-second (~30 m) elevation raster cropped directly from the global GLO-30 tile over the Balaghat AOI (`162 × 174` pixels in native EPSG:4326).

### Derived Terrain Derivatives (`data/derived/dem/balaghat/`)
Reprojected to **`EPSG:32644` (UTM Zone 44N)** with a metric cell size of **30.0 m × 30.0 m** (`168 × 168` pixels) so that topographic slopes and aspect gradients are calculated using true metric horizontal distances ($\Delta x, \Delta y$ in meters):

1. **`elevation.tif` (Elevation in meters):**
   * Projected surface elevation above sea level (EGM2008 datum).
   * Valid range: `295.85 m` to `559.43 m` (Mean: `312.76 m`, Median: `304.99 m`, Std: `25.83 m`).
2. **`slope.tif` (Slope in degrees):**
   * Calculated using Horn's 3×3 partial derivative finite-difference kernel:
     $$\text{Slope}^\circ = \arctan\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right) \times \frac{180^\circ}{\pi}$$
   * Valid range: `0.00°` to `89.70°` (Mean: `4.21°`, Median: `1.00°`, Std: `12.37°`).
3. **`aspect.tif` (Aspect / Slope Azimuth in degrees):**
   * Azimuth of maximum slope gradient ($0^\circ/360^\circ = \text{North}, 90^\circ = \text{East}, 180^\circ = \text{South}, 270^\circ = \text{West}$; flat areas assigned `-1.0`):
     $$\text{Aspect}^\circ = \left(90^\circ - \arctan2\left(\frac{\partial z}{\partial y}, -\frac{\partial z}{\partial x}\right) \times \frac{180^\circ}{\pi}\right) \pmod{360^\circ}$$
   * Mean directional aspect: `172.54°` (South-SSE regional dip).
4. **`hillshade.tif` (Analytical Shaded Relief intensity 0–255):**
   * Standard illumination: Solar Azimuth $315^\circ$ (Northwest), Solar Altitude $45^\circ$ (Zenith $45^\circ$):
     $$\text{Hillshade} = 255 \times \max(0, \cos(\text{Zenith})\cos(\text{Slope}) + \sin(\text{Zenith})\sin(\text{Slope})\cos(\text{Azimuth} - \text{Aspect}))$$
   * Valid range: `0.0` to `242.75` (Mean: `178.48`).

---

## 4. Grid Alignment & Nodata Metrics
* **Grid Dimensions:** `168 × 168` pixels
* **Valid Pixels:** `27,662` ($98.01\%$)
* **Nodata Pixels:** `562` ($1.99\%$, exterior reprojection margin corners tagged with `-9999.0`)
* **Spatial Alignment:** All 4 derived GeoTIFFs share exact identical dimensions, EPSG:32644 CRS, affine transform, and nodata masks.

---

## 5. Important Scientific Disclaimer & Data Governance
> **Scientific Notice:**
> These terrain layers are real physical geospatial measurements and geometric derivatives.
> - They are **NOT, by themselves, evidence of manganese mineralization**.
> - Topographical elevation differences reflect natural ridges, valleys, and pit benches, and must not be conflated with subsurface ore presence without ground-truth structural and geological assay correlation.
