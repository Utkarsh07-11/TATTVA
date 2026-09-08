# TATTVA — Real Data Architecture & Service Integration Layer

**Document Version:** 1.0.0  
**Phase:** Phase 7 Real Data Service Layer  
**Target Platform:** TATTVA Mining Intelligence Suite (MOIL Hackathon)  
**Data Status Model:** Strict Provenance Isolation (`real` | `derived` | `synthetic`)

---

## 1. Directory Structure and Physical Separation

TATTVA maintains an explicit, unbreachable separation between real government/audited datasets, analytical derived products, and legacy synthetic operational simulations.

```text
data/
├── real/                               # Authoritative primary source data (data_status: "real")
│   ├── moil/
│   │   ├── mines.csv                   # Audited 10-mine MOIL registry
│   │   ├── mine_locations.geojson      # Verified WGS84 point geometries
│   │   └── production/
│   │       ├── production_reported.csv # 11-year audited annual production (FY14-FY24)
│   │       └── source_manifest.json    # Full primary citation manifests
│   ├── sentinel2/
│   │   └── balaghat/                   # Copernicus Sentinel-2 Level-2A GeoTIFFs (UTM 44N)
│   └── dem/
│       └── balaghat/                   # Copernicus GLO-30 DEM GeoTIFF (UTM 44N)
│
├── derived/                            # Deterministic analytical transformations (data_status: "derived")
│   ├── sentinel2/
│   │   └── balaghat/                   # NDVI, NDWI, B4/B2, B11/B8 analytical rasters
│   ├── dem/
│   │   └── balaghat/                   # Slope, aspect, hillshade terrain models
│   └── production/
│       └── moil_annual_yoy_growth.csv  # Computed YoY % growth metrics
│
└── synthetic/                          # Legacy operational simulation (data_status: "synthetic")
    ├── production_daily.csv            # 3-block daily production simulation (Block A/B/C)
    ├── drillhole_assay.csv             # Synthetic 85-collar assay interval dataset
    ├── satellite_spectral_grid.csv     # Synthetic 20x20 grid proxy
    ├── mine_blocks.geojson             # Operational mine block boundary layout
    └── equipment_telemetry.csv         # Fleet equipment mechanical logs
```

---

## 2. Provenance and Data-Status Model

Every response, data loader, and frontend view carries an unambiguous provenance indicator:

1. **`data_status = "real"`**:
   - Primary data sourced directly from statutory filings, official corporate annual reports, IBM (Indian Minerals Yearbook), MoEFCC Environmental Clearance filings, or European Space Agency (ESA) Sentinel-2 Level-2A bottom-of-atmosphere reflectance acquisitions.
2. **`data_status = "derived"`**:
   - Analytical rasters or timeseries metrics computed via deterministic mathematical equations (e.g., $(B8-B4)/(B8+B4)$ for NDVI, Horn's algorithm for slope/aspect, percentage YoY growth) from real primary inputs.
3. **`data_status = "synthetic"`**:
   - Micro-level operational dispatch data, 3-block daily tonnage, and synthetic drillhole assays used exclusively to train and evaluate ML decision algorithms (LightGBM quantile forecaster, XGBoost prospectivity classifier, PuLP MILP dispatch optimizer).

---

## 3. Data Loader Architecture (`src/data/loader.py` & `src/data/registry.py`)

The data layer extends `DataLoader` without creating divergent incompatible loaders:

* **`RealDataRegistry` (`src/data/registry.py`)**:
  - Dynamically registers all dataset definitions (`moil_mines_csv`, `moil_mines_geojson`, `moil_production_reported`, `sentinel2_balaghat_raw`, `sentinel2_balaghat_derived`, `dem_balaghat_raw`, `dem_balaghat_derived`).
  - Evaluates physical filesystem availability (`Path.exists()`) on-demand rather than assuming file presence.
  - Exposes metadata without loading multi-megabyte GeoTIFF arrays into RAM.
* **`DataLoader` Extensions (`src/data/loader.py`)**:
  - `load_real_mines_df()`: Returns Pandas DataFrame of audited MOIL mines.
  - `load_real_mines_geojson()`: Returns GeoJSON FeatureCollection with audited coordinates and verification metadata.
  - `load_real_production_df()`: Returns historical statutory production records.
  - `get_mine_layer_availability(mine_id)`: Discovers GIS/raster layer availability for a given mine.

---

## 4. Backend API Endpoints (`src/api/routes/real_data.py`)

All real data endpoints are exposed under `/api/real/*`:

### 1. `GET /api/real/mines`
Returns the 10 audited MOIL operating mines.
```json
{
  "total": 10,
  "data_status": "real",
  "source": "data/real/moil/mines.csv",
  "mines": [
    {
      "mine_id": "MOIL_BALAGHAT",
      "mine_name": "Balaghat Mine",
      "state": "Madhya Pradesh",
      "district": "Balaghat",
      "latitude": 21.8464,
      "longitude": 80.2281,
      "coordinate_status": "VERIFIED_AUDITED",
      "coordinate_source": "MOIL / IBM / MoEFCC EC filings",
      "type": "Underground / Opencast",
      "status": "Operating",
      "data_status": "real"
    }
  ]
}
```

### 2. `GET /api/real/mines/{mine_id}`
Returns granular metadata and layer status for an individual mine. Returns `404` for non-existent IDs.

### 3. `GET /api/real/mines/{mine_id}/layers`
Dynamically inspects filesystem availability of analytical layers for the mine:
```json
{
  "mine_id": "MOIL_BALAGHAT",
  "data_status": "real",
  "layers": {
    "sentinel2_true_color": true,
    "ndvi": true,
    "ndwi": true,
    "red_nir_ratio": true,
    "swir_nir_ratio": true,
    "elevation": true,
    "slope": true,
    "aspect": true,
    "hillshade": true,
    "geology": false
  },
  "geology_status": "UNAVAILABLE",
  "geology_note": "Authoritative digitized GSI geology is currently unavailable for this AOI. Raw map acquisition remains blocked without user upload or authenticated Bhukosh session."
}
```

### 4. `GET /api/real/production`
Returns statutory annual production series with optional query parameters (`period`, `period_type`, `company`, `state`, `commodity`):
```json
{
  "total": 11,
  "data_status": "real",
  "provenance": {
    "source_file": "data/real/moil/production/production_reported.csv",
    "primary_sources": ["MOIL Official Annual Reports", "IBM Indian Minerals Yearbook"],
    "period_type": "annual",
    "commodity": "Manganese Ore"
  },
  "records": [
    {
      "financial_year": "2023-24",
      "production_lakh_tonnes": 17.56,
      "production_metric_tonnes": 1756000.0,
      "period_type": "annual",
      "source": "MOIL Annual Report 2023-24",
      "notes": "Audited statutory reported figure",
      "data_status": "real"
    }
  ]
}
```

### 5. `GET /api/real/rasters/summary`
Returns CRS, resolution, bounds, nodata, and dimensions for all registered GeoTIFF rasters via lightweight header reads.

---

## 5. Raster Handling & Security Safety

1. **Path Safety**: API endpoints do not accept arbitrary disk paths or filenames from clients. Queries only operate against pre-registered catalog keys.
2. **Lightweight Metadata**: GeoTIFF rasters are inspected via rasterio dataset headers (`src.profile`, `src.bounds`, `src.res`), consuming negligible memory without buffering multi-band arrays into RAM.
3. **Analytical GeoTIFF Authority**: Diagnostic PNGs in `data/real/sentinel2/balaghat/diagnostics/` serve strictly for visual inspection. The analytical `.tif` files in `data/real/` and `data/derived/` remain the sole authoritative numerical rasters.

---

## 6. Frontend Integration

1. **`DigitalMineMap.jsx`**:
   - Fetches the 10 audited MOIL mines from `/api/real/mines` on mount.
   - Includes a dedicated **MOIL Registry Selector** in the toolbar.
   - Panning/flying to any selected mine centers the map on verified statutory coordinates.
   - Real MOIL mine locations are plotted with gold/cyan markers carrying audited coordinate provenance popups.
   - Dedicated **Layer Catalog & Provenance Drawer** reveals the real-time availability of Sentinel-2, DEM, and terrain layers.
   - All synthetic block boundaries, ML prospectivity heatmap, drillhole collar assays, fleet GPS, and Survey of India boundary overlays remain fully functional.
2. **`ProductionAnalytics.jsx`**:
   - Features a mode switcher between **Operational Simulation (`data_status: synthetic`)** (30-day LightGBM quantile forecast) and **MOIL Reported Production (`data_status: real`)** (11-year statutory annual production series).
   - Real view renders annual production bars with YoY trend lines, metric cards (FY24 record high 17.56 Lakh Tonnes, 11-year average 12.38 Lakh Tonnes), and complete primary source citations.

---

## 7. Known Limitations & Blockers

1. **Authoritative Geology**: GSI Bhukosh interactive map download remains blocked pending authenticated GSI portal access or user-provided georeferenced maps. `geology: false` is accurately surfaced.
2. **Mine-Wise Daily Production**: MOIL reports production at the corporate/aggregate level in statutory annual reports. Daily operational dispatch by pit/block remains a synthetic benchmark for the LightGBM forecasting engine.
3. **Supervised Mineralization Labels**: Hard drillhole assay intersections and remote sensing proxies serve as prospectivity indicators; regional mineralization ground truth maps for all 10 mines require proprietary lease geological documentation.
