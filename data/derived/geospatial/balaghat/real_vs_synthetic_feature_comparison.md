# Real vs Synthetic Geospatial Feature Grid Comparison

**Document Purpose:** Comparative analysis between the real 30m derived feature grid (`data/derived/geospatial/balaghat/real_feature_grid.csv`) and the legacy synthetic grid (`data/synthetic/satellite_features_grid.csv`).

---

## 1. High-Level Comparison Table

| Attribute | Synthetic Dataset (`satellite_features_grid.csv`) | Real Dataset (`real_feature_grid.csv`) | Notes |
|---|---|---|---|
| **Data Status** | `synthetic` | `derived` (from `real` rasters) | Strict provenance separation |
| **Grid Resolution** | ~130 m irregular spacing | 30.0 m regular spacing | Real dataset has 22.5× higher spatial density |
| **Total Grid Cells** | 1,227 cells | 27,720 cells | Full 5 km × 5 km AOI coverage |
| **CRS / Projection** | Geographic WGS84 only (`latitude`, `longitude`) | Projected UTM 44N (`x`, `y`) + WGS84 (`lon`, `lat`) | Exact metric geometry for spatial analytics |
| **Primary Imagery Source** | None (mathematically simulated random distributions) | Copernicus Sentinel-2A Level-2A (ESA / AWS Open Data) | Real bottom-of-atmosphere surface reflectance |
| **Terrain Source** | None (Gaussian synthetic surfaces) | Copernicus Digital Elevation Model GLO-30 (30m) | Real EGM2008 geoid elevation & terrain models |

---

## 2. Feature-by-Feature Schema Mapping

| Feature Concept | Synthetic Column | Real Column | Status / Equivalence |
|---|---|---|---|
| **Grid Identifier** | `grid_id` (e.g. `GRID-0001`) | `cell_id` (e.g. `GRID-00001`) | Equivalent naming convention |
| **Coordinates** | `latitude`, `longitude` | `x`, `y`, `longitude`, `latitude` | Real includes both projected UTM meters and WGS84 |
| **Blue Band** | *None* | `B02` | Real Sentinel-2 band present |
| **Green Band** | *None* | `B03` | Real Sentinel-2 band present |
| **Red Band** | *None* | `B04` | Real Sentinel-2 band present |
| **NIR Band** | *None* | `B08` | Real Sentinel-2 band present |
| **SWIR1 Band** | *None* | `B11` | Real Sentinel-2 band present |
| **SWIR2 Band** | *None* | `B12` | Real Sentinel-2 band present |
| **Vegetation Index** | `ndvi` | `NDVI` | Real calculated from $(B08 - B04)/(B08 + B04)$ |
| **Water Index** | `ndwi` | `NDWI` | Real calculated from $(B03 - B08)/(B03 + B08)$ |
| **Iron Oxide Proxy** | `iron_oxide_index` | `red_nir_ratio` ($B04/B08$) | Real spectral ratio from calibrated BOA reflectance |
| **Clay Mineral Proxy**| `clay_index` | `swir_nir_ratio` ($B11/B08$) | Real spectral ratio from calibrated BOA reflectance |
| **Ferrous Mineral Index** | `ferrous_index` | *None* | Synthetic index with no direct uncalibrated S2 equivalent |
| **Land Surface Temp**| `lst_k` | *None* | S2 optical lacks thermal TIR sensor (requires Landsat/MODIS) |
| **Elevation** | `elevation_m` | `elevation` | Real Copernicus DEM GLO-30 orthometric height |
| **Slope** | `slope_deg` | `slope` | Real Horn's slope algorithm on Copernicus DEM |
| **Aspect** | `aspect_deg` | `aspect` | Real 360° azimuth from Copernicus DEM |
| **Hillshade** | *None* | `hillshade` | Real analytical terrain illumination (0-255 grayscale) |
| **Mine Distance** | *None* | `distance_to_moil_balaghat_m` | Real projected distance to audited MOIL Balaghat anchor |
| **Quality Metadata** | `synthetic` (boolean) | `valid_feature_fraction`, `feature_quality` | Granular multi-band data quality classification |

---

## 3. Scale and Value Differences

1. **Spectral Ratios**:
   - In the synthetic dataset, `iron_oxide_index` and `clay_index` were simulated around Gaussian means of ~1.2 with arbitrary variance.
   - In the real dataset, `red_nir_ratio` ($B04/B08$) and `swir_nir_ratio` ($B11/B08$) represent physical reflectance ratios from ESA Sentinel-2 Level-2A data, capturing real vegetation, soil, and bedrock spectral signatures.
2. **Topography**:
   - In the synthetic dataset, `elevation_m` ranged between 296 m and 420 m with smooth synthetic contours.
   - In the real dataset, `elevation` reflects actual Balaghat topography ranging from 295.8 m in the valley plains to 559.4 m along the ridge crests.
3. **No Land Surface Temperature in S2**:
   - The synthetic dataset included `lst_k` (~300–307 K). Sentinel-2 does not carry a thermal infrared sensor; thermal data requires Landsat-8/9 TIRS or MODIS. We do not invent fake thermal bands for Sentinel-2.

---

## 4. Operational Safety

- The legacy synthetic dataset (`data/synthetic/satellite_features_grid.csv`) remains completely untouched in its original location to maintain full backwards-compatibility with the existing synthetic prospectivity baseline.
- The real feature dataset is stored exclusively under `data/derived/geospatial/balaghat/` and carries explicit `data_status: "derived"` metadata.
