# Real Sentinel-2 Level-2A Remote-Sensing Baseline (Balaghat Mine AOI)

## 1. Overview & Dataset Purpose
This dataset establishes the first genuine, unauthenticated remote-sensing surface reflectance baseline for the **MOIL Balaghat Mine (Bharweli)** in the TATTVA platform (Phase 3).

The dataset is spatially anchored on the verified geodetic coordinates of **MOIL_BALAGHAT** (`21.8464° N, 80.2281° E`) from [`data/real/moil/mines.csv`](file:///G:/Tattvam/TATTVA/data/real/moil/mines.csv).

---

## 2. Area of Interest (AOI) Specification
* **Anchor Mine:** `MOIL_BALAGHAT` (Balaghat / Bharweli Mine, Madhya Pradesh)
* **Center Coordinate (WGS84):** `[80.2281° E, 21.8464° N]`
* **Bounding Box (WGS84 / EPSG:4326):**
  * `min_lon`: `80.2039° E`
  * `min_lat`: `21.8239° N`
  * `max_lon`: `80.2523° E`
  * `max_lat`: `21.8689° N`
* **AOI Dimensions:** `5.0 km × 5.0 km` (496 × 503 pixels at 10 m grid)
* **Definition File:** [`data/real/sentinel2/balaghat/aoi.geojson`](file:///G:/Tattvam/TATTVA/data/real/sentinel2/balaghat/aoi.geojson)

---

## 3. Satellite Scene & Acquisition Provenance
* **Data Source:** Copernicus Sentinel-2 (European Space Agency / AWS Earth Search Open Data STAC)
* **Product / Scene ID:** `S2A_44QMK_20240417_0_L2A`
* **Satellite Platform:** Sentinel-2A
* **Acquisition Timestamp:** `2024-04-17T05:22:46.341000Z`
* **Processing Level:** Level-2A (Bottom-of-Atmosphere Surface Reflectance, BOA)
* **Cloud Coverage:** `0.000325%` (essentially cloud-free scene)
* **Coordinate Reference System:** `EPSG:32644` (WGS 84 / UTM Zone 44N)
* **Access Method:** Windowed HTTP range requests on Cloud-Optimized GeoTIFFs (COGs) — zero credentials required.

---

## 4. Band Specifications & Resolution

| Band ID | Name | Central Wavelength (nm) | Native Resolution | Storage Location |
| :--- | :--- | :--- | :--- | :--- |
| `B02` | Blue | 492.4 | 10 m | `data/real/sentinel2/balaghat/raw/B02.tif` |
| `B03` | Green | 559.8 | 10 m | `data/real/sentinel2/balaghat/raw/B03.tif` |
| `B04` | Red | 664.6 | 10 m | `data/real/sentinel2/balaghat/raw/B04.tif` |
| `B08` | NIR | 832.8 | 10 m | `data/real/sentinel2/balaghat/raw/B08.tif` |
| `B11` | SWIR1 | 1610.4 | 20 m | `data/real/sentinel2/balaghat/raw/B11.tif` |
| `B12` | SWIR2 | 2185.7 | 20 m | `data/real/sentinel2/balaghat/raw/B12.tif` |
| `TCI` | True Color | RGB Composite | 10 m | `data/real/sentinel2/balaghat/raw/TCI.tif` |

### Resampling Method
* **Native 10 m Bands (`B02`, `B03`, `B04`, `B08`):** Preserved on their native 10 m grid.
* **Native 20 m Bands (`B11`, `B12`):** Stored in `raw/` at native 20 m resolution. For analytical spatial operations with 10 m bands (e.g. `swir_nir_ratio`), `B11` is resampled to the 10 m reference grid using **bilinear interpolation** (`rasterio.enums.Resampling.bilinear`).

---

## 5. Derived Features & Analytical Formulations
Stored in [`data/derived/sentinel2/balaghat/`](file:///G:/Tattvam/TATTVA/data/derived/sentinel2/balaghat/):

1. **Normalized Difference Vegetation Index (NDVI):**
   $$\text{NDVI} = \frac{\text{B08}_{\text{NIR}} - \text{B04}_{\text{RED}}}{\text{B08}_{\text{NIR}} + \text{B04}_{\text{RED}}}$$
   * Range: `[-0.3045, 0.8877]`, Mean: `0.5147`, Std: `0.1910`
   * File: `ndvi.tif`
2. **Normalized Difference Water Index (NDWI - McFeeters 1996):**
   $$\text{NDWI} = \frac{\text{B03}_{\text{GREEN}} - \text{B08}_{\text{NIR}}}{\text{B03}_{\text{GREEN}} + \text{B08}_{\text{NIR}}}$$
   * Range: `[-0.8135, 0.4058]`, Mean: `-0.4986`, Std: `0.1258`
   * File: `ndwi.tif`
3. **Red / NIR Spectral Ratio:**
   $$\text{Ratio}_{\text{Red/NIR}} = \frac{\text{B04}_{\text{RED}}}{\text{B08}_{\text{NIR}}}$$
   * Range: `[0.0595, 1.8757]`, Mean: `0.3431`, Std: `0.1824`
   * File: `red_nir_ratio.tif`
4. **SWIR1 / NIR Spectral Ratio:**
   $$\text{Ratio}_{\text{SWIR1/NIR}} = \frac{\text{B11}_{\text{SWIR1}}}{\text{B08}_{\text{NIR}}}$$
   * Range: `[0.3348, 4.4836]`, Mean: `0.9338`, Std: `0.3116`
   * File: `swir_nir_ratio.tif`

---

## 6. Diagnostic Visual Products
* **`true_color.png`:** 8-bit RGB composite (B04-B03-B02) stretched to 2nd-98th percentiles for visual spatial validation of pits, dumps, and drainage.
* **`ndvi.png`:** Color-mapped surface vegetation/alteration contrast map.

---

## 7. Important Scientific Disclaimer & Data Governance
> **Scientific Notice:**
> The derived spectral rasters (NDVI, NDWI, Red/NIR, SWIR/NIR) are purely **real remote-sensing biophysical indices**.
> - They **do NOT constitute proof of manganese mineralization** at this stage.
> - High or low index values reflect surface canopy density, soil moisture, and mineral reflectance, and must not be conflated with subsurface ore grade without ground-truth drillhole assay correlation.
