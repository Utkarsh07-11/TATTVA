"""
Real Data Registry for TATTVA
Provides centralized discovery, metadata tracking, and filesystem inspection
for authoritative (real), derived, and synthetic datasets.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional
import rasterio

from config.settings import settings


@dataclass
class DatasetDescriptor:
    dataset_id: str
    name: str
    dataset_type: str  # "tabular", "geojson", "raster_cog", "raster_geotiff"
    data_status: str   # "real", "derived", "synthetic"
    path: Path
    coverage: str
    crs: str
    resolution: str
    source_organization: str
    description: str

    @property
    def is_available(self) -> bool:
        return self.path.exists()


class RealDataRegistry:
    """Discovers and inspects real and derived datasets in the repository."""

    def __init__(self):
        self._descriptors: Dict[str, DatasetDescriptor] = {}
        self._register_known_datasets()

    def _register_known_datasets(self) -> None:
        real_dir = settings.REAL_DATA_DIR
        derived_dir = settings.DERIVED_DATA_DIR

        # 1. MOIL Mines Registry
        self.register(DatasetDescriptor(
            dataset_id="moil_mines_csv",
            name="MOIL 10-Mine Statutory Registry (CSV)",
            dataset_type="tabular",
            data_status="real",
            path=real_dir / "moil" / "mines.csv",
            coverage="Central India Manganese Belt (MP & Maharashtra)",
            crs="WGS84 (EPSG:4326)",
            resolution="Mine Portal Centroid Point",
            source_organization="Indian Bureau of Mines & Ministry of Mines",
            description="Audited statutory coordinates and metadata for MOIL's 10 operating mines."
        ))

        self.register(DatasetDescriptor(
            dataset_id="moil_mines_geojson",
            name="MOIL 10-Mine Statutory Registry (GeoJSON)",
            dataset_type="geojson",
            data_status="real",
            path=real_dir / "moil" / "mine_locations.geojson",
            coverage="Central India Manganese Belt (MP & Maharashtra)",
            crs="WGS84 (EPSG:4326)",
            resolution="Mine Portal Centroid Point",
            source_organization="Indian Bureau of Mines & MOIL Limited",
            description="GeoJSON FeatureCollection with statutory provenance tags."
        ))

        # 2. MOIL Reported Production
        self.register(DatasetDescriptor(
            dataset_id="moil_production_reported",
            name="MOIL Reported Historical Production",
            dataset_type="tabular",
            data_status="real",
            path=real_dir / "moil" / "production" / "production_reported.csv",
            coverage="MOIL Corporate Aggregate & State Totals",
            crs="N/A",
            resolution="Annual, Quarterly, and Monthly Disclosures",
            source_organization="MOIL Annual Reports & Ministry of Steel (PIB)",
            description="Audited 11-year annual series (FY16-FY26), quarterly releases, and IBM state baselines."
        ))

        self.register(DatasetDescriptor(
            dataset_id="moil_production_yoy",
            name="MOIL Annual YoY Production Growth Analytics",
            dataset_type="tabular",
            data_status="derived",
            path=derived_dir / "production" / "moil_annual_yoy_growth.csv",
            coverage="MOIL Corporate Timeline",
            crs="N/A",
            resolution="Annual Growth Rates (%)",
            source_organization="TATTVA Derived Analytics Engine",
            description="Calculated year-over-year production growth percentages from reported annual data."
        ))

        # 3. Sentinel-2 Imagery (Balaghat AOI)
        s2_real_dir = real_dir / "sentinel2" / "balaghat" / "raw"
        for band in ["B02", "B03", "B04", "B08", "B11", "B12", "TCI"]:
            res_str = "10m" if band in ["B02", "B03", "B04", "B08", "TCI"] else "20m"
            self.register(DatasetDescriptor(
                dataset_id=f"sentinel2_raw_{band.lower()}",
                name=f"Sentinel-2 L2A BOA Reflectance ({band})",
                dataset_type="raster_cog",
                data_status="real",
                path=s2_real_dir / f"{band}.tif",
                coverage="Balaghat Mine AOI (5 km x 5 km)",
                crs="UTM Zone 44N (EPSG:32644)",
                resolution=res_str,
                source_organization="European Space Agency (ESA) Copernicus Programme",
                description=f"Raw surface reflectance band {band} clipped to Balaghat AOI."
            ))

        # 4. Sentinel-2 Derived Indices
        s2_der_dir = derived_dir / "sentinel2" / "balaghat"
        for idx, title, desc in [
            ("ndvi", "Normalized Difference Vegetation Index (NDVI)", "Surface vegetation index (B08-B04)/(B08+B04)."),
            ("ndwi", "Normalized Difference Water Index (NDWI)", "Water and moisture index (B03-B08)/(B03+B08)."),
            ("red_nir_ratio", "Red / NIR Band Ratio", "Iron oxide alteration proxy (B04/B08)."),
            ("swir_nir_ratio", "SWIR / NIR Band Ratio", "Hydrothermal clay/carbonate proxy (B11/B08).")
        ]:
            self.register(DatasetDescriptor(
                dataset_id=f"sentinel2_derived_{idx}",
                name=title,
                dataset_type="raster_geotiff",
                data_status="derived",
                path=s2_der_dir / f"{idx}.tif",
                coverage="Balaghat Mine AOI (5 km x 5 km)",
                crs="UTM Zone 44N (EPSG:32644)",
                resolution="10m",
                source_organization="TATTVA Geospatial Engine (from ESA Sentinel-2)",
                description=desc
            ))

        # 5. Copernicus DEM (Balaghat AOI)
        dem_real_file = real_dir / "dem" / "balaghat" / "raw" / "copernicus_dem_30m_balaghat.tif"
        self.register(DatasetDescriptor(
            dataset_id="copernicus_dem_raw",
            name="Copernicus DEM GLO-30 Raw Surface Model",
            dataset_type="raster_cog",
            data_status="real",
            path=dem_real_file,
            coverage="Balaghat Mine AOI (5 km x 5 km)",
            crs="WGS84 (EPSG:4326)",
            resolution="1 arc-second (~30m)",
            source_organization="European Space Agency (ESA) & Airbus Defence",
            description="Unmodified GLO-30 digital surface model tile subset."
        ))

        # 6. DEM Derived Terrain Features
        dem_der_dir = derived_dir / "dem" / "balaghat"
        for feature, title, desc in [
            ("elevation", "Projected Surface Elevation (m)", "UTM44N metric projected elevation in meters above sea level."),
            ("slope", "Topographic Slope (Degrees)", "Horn algorithm finite-difference terrain slope (0-90 degrees)."),
            ("aspect", "Slope Aspect / Azimuth (Degrees)", "Directional azimuth of maximum slope gradient (0-360 degrees)."),
            ("hillshade", "Analytical Shaded Relief", "Illuminated shaded relief intensity (0-255) at 315/45 illumination.")
        ]:
            self.register(DatasetDescriptor(
                dataset_id=f"dem_derived_{feature}",
                name=title,
                dataset_type="raster_geotiff",
                data_status="derived",
                path=dem_der_dir / f"{feature}.tif",
                coverage="Balaghat Mine AOI (5 km x 5 km)",
                crs="UTM Zone 44N (EPSG:32644)",
                resolution="30m",
                source_organization="TATTVA Geospatial Engine (from Copernicus DEM)",
                description=desc
            ))

        # 7. Derived Real Geospatial Feature Grid (30m)
        self.register(DatasetDescriptor(
            dataset_id="balaghat_real_feature_grid_30m",
            name="Balaghat 30m Real Geospatial Feature Grid",
            dataset_type="tabular",
            data_status="derived",
            path=derived_dir / "geospatial" / "balaghat" / "real_feature_grid.csv",
            coverage="Balaghat Mine AOI (5 km x 5 km)",
            crs="UTM Zone 44N (EPSG:32644) + WGS84",
            resolution="30.0m regular grid (27,720 cells)",
            source_organization="TATTVA Feature Extraction Pipeline (ESA Sentinel-2 + Copernicus DEM)",
            description="ML-ready regular feature dataset sampling 14 real remote-sensing and terrain layers."
        ))

    def register(self, descriptor: DatasetDescriptor) -> None:
        self._descriptors[descriptor.dataset_id] = descriptor

    def get_descriptor(self, dataset_id: str) -> Optional[DatasetDescriptor]:
        return self._descriptors.get(dataset_id)

    def list_descriptors(self) -> List[DatasetDescriptor]:
        return list(self._descriptors.values())

    def get_raster_metadata(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        desc = self.get_descriptor(dataset_id)
        if not desc or not desc.path.exists() or desc.dataset_type not in ("raster_cog", "raster_geotiff"):
            return None

        with rasterio.open(desc.path) as src:
            bounds = src.bounds
            crs_code = src.crs.to_string() if src.crs else "Unknown"
            return {
                "dataset_id": desc.dataset_id,
                "name": desc.name,
                "data_status": desc.data_status,
                "dataset_type": desc.dataset_type,
                "dimensions": {"height": src.height, "width": src.width, "bands": src.count},
                "crs": crs_code,
                "resolution": [float(src.res[0]), float(src.res[1])],
                "bounds": [float(bounds.left), float(bounds.bottom), float(bounds.right), float(bounds.top)],
                "nodata": float(src.nodata) if src.nodata is not None else None,
                "source_organization": desc.source_organization,
                "description": desc.description,
                "available": True
            }


real_data_registry = RealDataRegistry()
