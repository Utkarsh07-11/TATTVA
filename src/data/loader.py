"""
Data Loading & Caching Engine for SIH 2026 PS 26009
Loads and parses CSVs, GeoJSONs, and JSON manifests from data directories, running validation checks.
Strictly separates Real, Source-Derived (DSR 2022), Derived, and Synthetic/Simulation layers.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd

from config.settings import settings
from src.data.validator import DataValidator


class DataLoader:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or settings.PROCESSED_DATA_DIR
        self._production_df: Optional[pd.DataFrame] = None
        self._equipment_df: Optional[pd.DataFrame] = None
        self._drillhole_df: Optional[pd.DataFrame] = None
        self._satellite_df: Optional[pd.DataFrame] = None
        self._mine_blocks_geojson: Optional[Dict[str, Any]] = None
        self._real_prospectivity_geojson: Optional[Dict[str, Any]] = None
        self._real_mineralization_evidence_geojson: Optional[Dict[str, Any]] = None

        # DSR 2022 Caches
        self._dsr_manifest: Optional[Dict[str, Any]] = None
        self._dsr_mines_df: Optional[pd.DataFrame] = None
        self._dsr_lease_areas_df: Optional[pd.DataFrame] = None
        self._dsr_boundary_pillars_df: Optional[pd.DataFrame] = None
        self._dsr_boundaries_geojson: Optional[Dict[str, Any]] = None
        self._dsr_geology_df: Optional[pd.DataFrame] = None
        self._dsr_grade_df: Optional[pd.DataFrame] = None
        self._dsr_exploration_df: Optional[pd.DataFrame] = None
        self._dsr_production_df: Optional[pd.DataFrame] = None
        self._dsr_mine_plan_df: Optional[pd.DataFrame] = None
        self._dsr_constraints_df: Optional[pd.DataFrame] = None

    def load_production_data(self, force_reload: bool = False) -> pd.DataFrame:
        if self._production_df is None or force_reload:
            file_path = self.data_dir / "production_daily.csv"
            if not file_path.exists():
                file_path = settings.SYNTHETIC_DATA_DIR / "production_daily.csv"
            df = pd.read_csv(file_path)
            df["date"] = pd.to_datetime(df["date"])
            valid, errors = DataValidator.validate_production(df)
            if not valid:
                raise ValueError(f"Production data validation failed: {errors}")
            self._production_df = df
        return self._production_df.copy()

    def load_equipment_events(self, force_reload: bool = False) -> pd.DataFrame:
        if self._equipment_df is None or force_reload:
            file_path = self.data_dir / "equipment_events.csv"
            if not file_path.exists():
                file_path = settings.SYNTHETIC_DATA_DIR / "equipment_events.csv"
            df = pd.read_csv(file_path)
            df["start_time"] = pd.to_datetime(df["start_time"])
            df["end_time"] = pd.to_datetime(df["end_time"])
            self._equipment_df = df
        return self._equipment_df.copy()

    def load_drillhole_assay(self, force_reload: bool = False) -> pd.DataFrame:
        if self._drillhole_df is None or force_reload:
            file_path = self.data_dir / "drillhole_assay.csv"
            if not file_path.exists():
                file_path = settings.SYNTHETIC_DATA_DIR / "drillhole_assay.csv"
            df = pd.read_csv(file_path)
            valid, errors = DataValidator.validate_drillholes(df)
            if not valid:
                raise ValueError(f"Drillhole data validation failed: {errors}")
            self._drillhole_df = df
        return self._drillhole_df.copy()

    def load_satellite_grid(self, force_reload: bool = False) -> pd.DataFrame:
        if self._satellite_df is None or force_reload:
            file_path = self.data_dir / "satellite_features_grid.csv"
            if not file_path.exists():
                file_path = settings.SYNTHETIC_DATA_DIR / "satellite_features_grid.csv"
            df = pd.read_csv(file_path)
            valid, errors = DataValidator.validate_satellite_grid(df)
            if not valid:
                raise ValueError(f"Satellite grid data validation failed: {errors}")
            self._satellite_df = df
        return self._satellite_df.copy()

    def load_mine_blocks_geojson(self, force_reload: bool = False) -> Dict[str, Any]:
        if self._mine_blocks_geojson is None or force_reload:
            file_path = self.data_dir / "mine_blocks.geojson"
            if not file_path.exists():
                file_path = settings.SYNTHETIC_DATA_DIR / "mine_blocks.geojson"
            with open(file_path, "r", encoding="utf-8") as f:
                self._mine_blocks_geojson = json.load(f)
        return self._mine_blocks_geojson

    # --- Real Data Service Access Methods ---

    def load_real_mines_df(self) -> pd.DataFrame:
        """Loads the audited MOIL 10-mine statutory registry."""
        mines_csv = settings.REAL_DATA_DIR / "moil" / "mines.csv"
        if not mines_csv.exists():
            raise FileNotFoundError(f"Real MOIL mines CSV not found at {mines_csv}")
        df = pd.read_csv(mines_csv)
        df["data_status"] = "real"
        return df

    def load_real_mines_geojson(self) -> Dict[str, Any]:
        """Loads the audited MOIL 10-mine GeoJSON feature collection."""
        geojson_file = settings.REAL_DATA_DIR / "moil" / "mine_locations.geojson"
        if not geojson_file.exists():
            raise FileNotFoundError(f"Real MOIL mine locations GeoJSON not found at {geojson_file}")
        with open(geojson_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("metadata", {})
        data["metadata"]["data_status"] = "real"
        return data

    def load_real_production_df(
        self,
        period: Optional[str] = None,
        period_type: Optional[str] = None,
        company: Optional[str] = None,
        state: Optional[str] = None,
        commodity: Optional[str] = None
    ) -> pd.DataFrame:
        """Loads reported historical production with optional filtering."""
        prod_csv = settings.REAL_DATA_DIR / "moil" / "production" / "production_reported.csv"
        if not prod_csv.exists():
            raise FileNotFoundError(f"Reported production CSV not found at {prod_csv}")
        df = pd.read_csv(prod_csv)

        if period:
            df = df[df["period"].str.lower() == period.lower()]
        if period_type:
            df = df[df["period_type"].str.lower() == period_type.lower()]
        if company:
            df = df[df["company"].str.lower() == company.lower()]
        if state:
            df = df[df["state"].str.lower() == state.lower()]
        if commodity:
            df = df[df["commodity"].str.lower() == commodity.lower()]

        return df.copy()

    def get_mine_layer_availability(self, mine_id: str) -> Dict[str, Any]:
        """
        Dynamically detects available real geospatial layers for a given mine ID.
        Checks real data directories on the filesystem.
        """
        mines_df = self.load_real_mines_df()
        norm_id = mine_id.strip().upper()
        match = mines_df[
            (mines_df["mine_id"].str.upper() == norm_id) |
            (mines_df["mine_name"].str.upper() == norm_id)
        ]
        if match.empty:
            return {"exists": False, "mine_id": mine_id, "layers": {}}

        row = match.iloc[0]
        actual_id = str(row["mine_id"])
        is_balaghat = (actual_id == "MOIL_BALAGHAT")

        # Filesystem layer presence detection
        s2_der_dir = settings.DERIVED_DATA_DIR / "sentinel2" / "balaghat"
        dem_der_dir = settings.DERIVED_DATA_DIR / "dem" / "balaghat"
        dsr_boundary_file = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "boundaries.geojson"

        layers = {
            "sentinel2_true_color": is_balaghat and (s2_der_dir / "true_color.png").exists(),
            "ndvi": is_balaghat and (s2_der_dir / "ndvi.tif").exists(),
            "ndwi": is_balaghat and (s2_der_dir / "ndwi.tif").exists(),
            "red_nir_ratio": is_balaghat and (s2_der_dir / "red_nir_ratio.tif").exists(),
            "swir_nir_ratio": is_balaghat and (s2_der_dir / "swir_nir_ratio.tif").exists(),
            "elevation": is_balaghat and (dem_der_dir / "elevation.tif").exists(),
            "slope": is_balaghat and (dem_der_dir / "slope.tif").exists(),
            "aspect": is_balaghat and (dem_der_dir / "aspect.tif").exists(),
            "hillshade": is_balaghat and (dem_der_dir / "hillshade.tif").exists(),
            "dsr_lease_boundary": dsr_boundary_file.exists() and (actual_id in ("MOIL_BALAGHAT", "MOIL_UKWA")),
            "geology": False  # Blocked pending full vector polygon cadastre
        }

        return {
            "exists": True,
            "mine_id": actual_id,
            "mine_name": str(row["mine_name"]),
            "state": str(row["state"]),
            "district": str(row["district"]),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "point_type": str(row.get("point_type", "mine_site_reference")),
            "verification_status": str(row["verification_status"]),
            "layers": layers,
            "data_status": "real"
        }

    def get_mine_capability_matrix(self) -> Dict[str, Any]:
        """
        Dynamically audits all 10 registered MOIL mines against filesystem and dataset artifacts.
        Evaluates dimension-level capabilities with strict status semantics:
        REAL, SOURCE-DERIVED, DERIVED, EXPERIMENTAL, SIMULATION, UNAVAILABLE, UNAVAILABLE_FOR_MINE.
        """
        mines_df = self.load_real_mines_df()
        matrix = []

        for _, row in mines_df.iterrows():
            mine_id = str(row["mine_id"])
            mine_name = str(row["mine_name"])
            state = str(row["state"])
            district = str(row["district"])
            is_balaghat = (mine_id == "MOIL_BALAGHAT")
            is_balaghat_district = (district.lower() == "balaghat")

            # 1. Registry status
            registry_status = "REAL"

            # 2. Coordinate status
            v_status = str(row.get("verification_status", ""))
            coord_status = "REAL" if "statutory" in v_status or "surveyed" in v_status else "SOURCE-DERIVED"

            # 3. Geometry status
            geometry_status = "UNAVAILABLE"  # Surveyed closed DGPS boundary polygons unavailable pending statutory release

            # 4. Satellite status
            layer_info = self.get_mine_layer_availability(mine_id)
            layers = layer_info.get("layers", {})
            satellite_status = "REAL" if layers.get("sentinel2_true_color") else "UNAVAILABLE_FOR_MINE"

            # 5. Terrain status
            terrain_status = "REAL" if layers.get("elevation") else "UNAVAILABLE_FOR_MINE"

            # 6. Geology status (DSR stratigraphy)
            geology_status = "SOURCE-DERIVED" if is_balaghat_district else "UNAVAILABLE_FOR_MINE"

            # 7. Exploration status
            if is_balaghat:
                exploration_status = "EXPERIMENTAL"  # Phase 9B 30m grid ensemble surface
            elif is_balaghat_district:
                exploration_status = "SOURCE-DERIVED"  # Aggregate DSR drilling counts & UNFC reserves
            else:
                exploration_status = "UNAVAILABLE_FOR_MINE"

            # 8. Production status
            production_status = "REAL"  # Company-level reported series; DSR for district

            # 9. Mine plan status
            mine_plan_status = "SOURCE-DERIVED" if is_balaghat_district else "UNAVAILABLE_FOR_MINE"

            # 10. Constraint status
            try:
                c_df = self.load_dsr_constraints(mine_id=mine_id)
                has_constraints = not c_df.empty
                has_operational_constraints = not c_df[c_df["constraint_category"] != "environmental"].empty
            except Exception:
                has_constraints = False
                has_operational_constraints = False
            constraint_status = "SOURCE-DERIVED" if has_constraints else "UNAVAILABLE_FOR_MINE"

            # 11. Simulation status (Strict rule: only Balaghat / Block A has qualified operational telemetry)
            simulation_status = "SIMULATION" if is_balaghat else "UNAVAILABLE_FOR_MINE"

            # 12. Optimization status (Strict rule: requires simulation + decision variables + constraints)
            optimization_status = "OPTIMIZATION" if (is_balaghat and has_constraints) else "UNAVAILABLE_FOR_MINE"

            # Derive Tier and Workflow Status
            if is_balaghat:
                tier = "LEVEL_A"
                workflow_status = "FULL_DECISION_WORKFLOW"
                level_description = "Full decision workflow available (Remote Sensing + Terrain + DSR Context + Phase 9B Exploration + Operational Simulation + SHAP + Optimization)."
            elif is_balaghat_district and has_operational_constraints:
                tier = "LEVEL_B"
                workflow_status = "PARTIAL_DECISION_WORKFLOW"
                level_description = "Partial decision workflow available (DSR Stratigraphy + Concession Evidence + Mining Constraints). Exploration rasters and operational simulation UNAVAILABLE_FOR_MINE."
            elif is_balaghat_district:
                tier = "LEVEL_C"
                workflow_status = "CONTEXT_ONLY"
                level_description = "Contextual intelligence only (DSR Stratigraphy & Concession Reference). Exploration rasters, operational simulation, and optimization UNAVAILABLE_FOR_MINE."
            else:
                tier = "LEVEL_D"
                workflow_status = "REGISTRY_REFERENCE_ONLY"
                level_description = "Registry and reference context only (Audited WGS84 Coordinates & Company Production). DSR, exploration, and operational simulation UNAVAILABLE_FOR_MINE."

            matrix.append({
                "mine_id": mine_id,
                "mine_name": mine_name,
                "state": state,
                "district": district,
                "tier": tier,
                "decision_workflow_status": workflow_status,
                "level_description": level_description,
                "capabilities": {
                    "registry_status": registry_status,
                    "coordinate_status": coord_status,
                    "geometry_status": geometry_status,
                    "satellite_status": satellite_status,
                    "terrain_status": terrain_status,
                    "geology_status": geology_status,
                    "exploration_status": exploration_status,
                    "production_status": production_status,
                    "mine_plan_status": mine_plan_status,
                    "constraint_status": constraint_status,
                    "simulation_status": simulation_status,
                    "optimization_status": optimization_status,
                    "decision_workflow_status": workflow_status
                },
                "data_status": "real_registry_backed"
            })

        return {
            "total_mines": len(matrix),
            "data_status": "real",
            "matrix": matrix
        }

    def get_mine_dashboard_summary(self, mine_id: str) -> Dict[str, Any]:
        """
        Consolidated metadata and Data Availability Status for a selected MOIL mine.
        Derives state dynamically from the authoritative registry without hardcoding.
        Exposes dimension-level capability statuses and tier classifications.
        """
        mines_df = self.load_real_mines_df()
        norm_id = mine_id.strip().upper()
        match = mines_df[
            (mines_df["mine_id"].str.upper() == norm_id) |
            (mines_df["mine_name"].str.upper() == norm_id)
        ]
        if match.empty:
            return {
                "exists": False,
                "mine_id": mine_id,
                "message": f"Mine '{mine_id}' not found in the audited MOIL statutory registry."
            }

        row = match.iloc[0]
        actual_id = str(row["mine_id"])
        is_balaghat = (actual_id == "MOIL_BALAGHAT")
        is_balaghat_district = (str(row["district"]).lower() == "balaghat")

        # Layer presence
        layer_info = self.get_mine_layer_availability(actual_id)
        layers = layer_info.get("layers", {})

        # Constraint presence
        try:
            c_df = self.load_dsr_constraints(mine_id=actual_id)
            has_constraints = not c_df.empty
            has_operational_constraints = not c_df[c_df["constraint_category"] != "environmental"].empty
        except Exception:
            has_constraints = False
            has_operational_constraints = False

        # Tier & capabilities
        if is_balaghat:
            tier = "LEVEL_A"
            workflow_status = "FULL_DECISION_WORKFLOW"
        elif is_balaghat_district and has_operational_constraints:
            tier = "LEVEL_B"
            workflow_status = "PARTIAL_DECISION_WORKFLOW"
        elif is_balaghat_district:
            tier = "LEVEL_C"
            workflow_status = "CONTEXT_ONLY"
        else:
            tier = "LEVEL_D"
            workflow_status = "REGISTRY_REFERENCE_ONLY"

        # Build 5 categories of the Data Availability Framework
        data_availability = {
            "real_data": [
                {
                    "category": "REAL DATA",
                    "name": "Multispectral Satellite Imagery",
                    "resource": "Sentinel-2A L2A (10m-20m)",
                    "status": "AVAILABLE" if layers.get("sentinel2_true_color") else "UNAVAILABLE_FOR_MINE",
                    "source": "ESA Copernicus (2024-04-17)",
                    "coverage": "5km x 5km Balaghat AOI" if is_balaghat else "Not acquired for this mine"
                },
                {
                    "category": "REAL DATA",
                    "name": "Digital Elevation Model",
                    "resource": "Copernicus DEM GLO-30 (30m)",
                    "status": "AVAILABLE" if layers.get("elevation") else "UNAVAILABLE_FOR_MINE",
                    "source": "ESA / Airbus WorldDEM",
                    "coverage": "5km x 5km Balaghat AOI" if is_balaghat else "Not acquired for this mine"
                }
            ],
            "source_derived_data": [
                {
                    "category": "SOURCE-DERIVED",
                    "name": "Balaghat District Survey Report (DSR 2022)",
                    "resource": "Statutory Mine Leases, Khasra Cadastre & Boundary Pillars",
                    "status": "AVAILABLE" if is_balaghat_district else "UNAVAILABLE_FOR_MINE",
                    "source": "Directorate of Geology and Mining MP / Balaghat DSR 2022",
                    "coverage": f"Leasehold in {row.get('tehsil', 'Balaghat')} Tehsil" if is_balaghat_district else "Outside Balaghat District"
                }
            ],
            "reported_data": [
                {
                    "category": "REPORTED DATA",
                    "name": "MOIL Statutory Production",
                    "resource": "Audited Company-Level Production Series",
                    "status": "AVAILABLE_AGGREGATE",
                    "grain": "Annual (FY 2013-14 to FY 2023-24)",
                    "scope_note": "Company-level aggregate reported production. Mine-level historical production is separated under DSR records.",
                    "source": "MOIL Limited Statutory Annual Reports & IBM Yearbooks"
                }
            ],
            "experimental": [
                {
                    "category": "EXPERIMENTAL",
                    "name": "Real Exploration Priority Heuristic",
                    "resource": "Phase 9B Exploration Prioritization Experiment (30m grid)",
                    "status": "AVAILABLE" if is_balaghat else "UNAVAILABLE_FOR_MINE",
                    "cells": 27720 if is_balaghat else 0,
                    "disclaimer": "Relative ranking heuristic, not probability. No independent negative drillholes available.",
                    "scope": "Balaghat AOI (5km x 5km)" if is_balaghat else "Real exploration-priority experiment is currently available only for Balaghat."
                }
            ],
            "simulation": [
                {
                    "category": "SIMULATION",
                    "name": "TATTVA Operational Simulation",
                    "resource": "Parametric Pit Scheduling & Fleet Dispatch Telemetry",
                    "status": "SIMULATION" if is_balaghat else "UNAVAILABLE_FOR_MINE",
                    "scope_note": "Synthetic operational simulation for decision-support modeling. Not MOIL historical telemetry." if is_balaghat else "Operational shift simulation unavailable for this mine.",
                    "source": "TATTVA Parametric Simulation Engine"
                }
            ],
            "unavailable": [
                {
                    "category": "UNAVAILABLE",
                    "name": "Authoritative Geological Vector Layer",
                    "resource": "Digital Bedrock Lithology & Structural Strike Vectors",
                    "status": "UNAVAILABLE",
                    "reason": "Official GSI 1:50k vector map pending release in public domain."
                }
            ]
        }

        return {
            "exists": True,
            "mine_id": actual_id,
            "mine_name": str(row["mine_name"]),
            "company": str(row["company"]),
            "state": str(row["state"]),
            "district": str(row["district"]),
            "mineral": str(row["mineral"]),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "point_type": str(row.get("point_type", "mine_site_reference")),
            "tehsil": str(row.get("tehsil", "")),
            "lease_area_ha": float(row.get("lease_area_ha", 0.0)) if pd.notna(row.get("lease_area_ha")) else None,
            "verification_status": str(row["verification_status"]),
            "coordinate_interpretation": str(row["coordinate_interpretation"]),
            "coordinate_precision": str(row["coordinate_precision"]),
            "source_title": str(row["source_title"]),
            "source_url": str(row["source_url"]),
            "evidence_notes": str(row["evidence_notes"]),
            "layers": layers,
            "capability_tier": tier,
            "decision_workflow_status": workflow_status,
            "data_availability_status": data_availability,
            "exploration_available": is_balaghat,
            "simulation_available": is_balaghat,
            "optimization_available": (is_balaghat and has_constraints),
            "data_status": "real_registry_backed"
        }

    def load_real_feature_grid(self, quality_filter: Optional[str] = None) -> pd.DataFrame:
        """
        Loads the derived 30m real geospatial feature grid for Balaghat AOI.
        """
        grid_csv = settings.DERIVED_DATA_DIR / "geospatial" / "balaghat" / "real_feature_grid.csv"
        if not grid_csv.exists():
            raise FileNotFoundError(f"Real feature grid not found at {grid_csv}")
        df = pd.read_csv(grid_csv)
        if quality_filter:
            df = df[df["feature_quality"].str.lower() == quality_filter.lower()]
        return df.copy()

    def load_real_prospectivity_meta(self, mine_id: str = "MOIL_BALAGHAT") -> Dict[str, Any]:
        """
        Loads and returns the Phase 9B real prospectivity experiment metadata and summary.
        """
        norm_id = mine_id.strip().upper()
        if norm_id != "MOIL_BALAGHAT":
            return {
                "mine_id": mine_id,
                "is_available": False,
                "data_status": "unavailable",
                "message": f"Real prospectivity experiment is not yet available for mine '{mine_id}'. Available only for MOIL_BALAGHAT."
            }

        meta_file = settings.DERIVED_DATA_DIR / "geospatial" / "balaghat" / "prospectivity_experiment_metadata.json"
        summary_file = settings.DERIVED_DATA_DIR / "geospatial" / "balaghat" / "prospectivity_experiment_summary.json"

        if not meta_file.exists() or not summary_file.exists():
            raise FileNotFoundError("Phase 9B prospectivity experiment metadata or summary JSON not found.")

        with open(meta_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        with open(summary_file, "r", encoding="utf-8") as f:
            summary = json.load(f)

        return {
            "mine_id": "MOIL_BALAGHAT",
            "mine_name": "Balaghat (Bharweli) Underground Mine",
            "is_available": True,
            "data_status": "derived_from_real_data",
            "experiment_id": metadata.get("experiment_id", "balaghat_real_prospectivity_phase9b"),
            "execution_timestamp": metadata.get("execution_timestamp"),
            "grid_resolution_m": 30.0,
            "crs": "EPSG:32644",
            "total_cells": summary.get("dataset_summary", {}).get("total_cells", 27720),
            "valid_cells": summary.get("dataset_summary", {}).get("valid_cells", 27487),
            "partial_cells": summary.get("dataset_summary", {}).get("partial_cells", 233),
            "features_used": metadata.get("preprocessing", {}).get("features_used", []),
            "feature_count": len(metadata.get("preprocessing", {}).get("features_used", [])),
            "model_algorithms": metadata.get("model_algorithms", {}),
            "score_distributions": summary.get("score_distributions", {}),
            "spatial_cluster_statistics": summary.get("spatial_cluster_statistics", {}),
            "known_site_sanity_check": summary.get("known_site_sanity_check", {}),
            "model_agreement_top_k": summary.get("model_agreement_top_k", {}),
            "critical_scientific_limitations": metadata.get("critical_scientific_limitations", []),
            "available_layers": [
                {
                    "id": "exploration_priority_score",
                    "name": "Real Exploration Priority",
                    "description": "Ensemble rank aggregation heuristic combining anomaly, robust distance, and anchor similarity.",
                    "scale": [0.0, 1.0],
                    "is_default": True
                },
                {
                    "id": "anomaly_score",
                    "name": "Spectral/Terrain Anomaly",
                    "description": "Unsupervised tree-isolation multi-spectral and terrain anomaly score.",
                    "scale": [0.0, 1.0],
                    "is_default": False
                },
                {
                    "id": "robust_distance_score",
                    "name": "Robust Multivariate Distance",
                    "description": "PCA-decorrelated robust Mahalanobis distance from AOI feature centroid.",
                    "scale": [0.0, 1.0],
                    "is_default": False
                },
                {
                    "id": "positive_anchor_similarity",
                    "name": "Bharweli Anchor Similarity",
                    "description": "One-class standardized Euclidean distance / exponential similarity to verified Bharweli shaft portal.",
                    "scale": [0.0, 1.0],
                    "is_default": False
                }
            ],
            "provenance": {
                "remote_sensing": "Sentinel-2A Level-2A (ESA Copernicus, 2024-04-17)",
                "terrain": "Copernicus DEM GLO-30 (ESA/Airbus, 30m)",
                "site_evidence": "Ministry of Environment (MoEFCC PARIVESH) & GSI Memoir Series",
                "methodology": "Phase 9B Real-Data Prospectivity Experiment (Unsupervised + Positive-Anchor Similarity)"
            }
        }

    def load_real_prospectivity_geojson(self, mine_id: str = "MOIL_BALAGHAT") -> Dict[str, Any]:
        """
        Lazily builds and caches the 27,720-cell GeoJSON FeatureCollection of 30m grid polygons.
        """
        norm_id = mine_id.strip().upper()
        if norm_id != "MOIL_BALAGHAT":
            return {
                "type": "FeatureCollection",
                "metadata": {
                    "mine_id": mine_id,
                    "is_available": False,
                    "data_status": "unavailable",
                    "message": f"Real prospectivity GeoJSON is not available for mine '{mine_id}'."
                },
                "features": []
            }

        if self._real_prospectivity_geojson is not None:
            return self._real_prospectivity_geojson

        csv_path = settings.DERIVED_DATA_DIR / "geospatial" / "balaghat" / "prospectivity_experiment.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Prospectivity experiment CSV not found at {csv_path}")

        df = pd.read_csv(csv_path)

        # Approximate 30m half-step in degrees WGS84
        half_lon = 0.0002903 / 2.0
        half_lat = 0.0002713 / 2.0

        features = []
        for row in df.itertuples():
            lon = float(row.longitude)
            lat = float(row.latitude)
            coords = [[
                [round(lon - half_lon, 6), round(lat - half_lat, 6)],
                [round(lon + half_lon, 6), round(lat - half_lat, 6)],
                [round(lon + half_lon, 6), round(lat + half_lat, 6)],
                [round(lon - half_lon, 6), round(lat + half_lat, 6)],
                [round(lon - half_lon, 6), round(lat - half_lat, 6)],
            ]]

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": coords
                },
                "properties": {
                    "cell_id": str(row.cell_id),
                    "exploration_priority_score": float(row.exploration_priority_score),
                    "anomaly_score": float(row.anomaly_score),
                    "robust_distance_score": float(row.robust_distance_score),
                    "positive_anchor_similarity": float(row.positive_anchor_similarity),
                    "feature_quality": str(row.feature_quality)
                }
            })

        self._real_prospectivity_geojson = {
            "type": "FeatureCollection",
            "metadata": {
                "mine_id": "MOIL_BALAGHAT",
                "data_status": "derived_from_real_data",
                "total_features": len(features),
                "grid_resolution_m": 30.0,
                "scientific_disclaimer": "Relative exploration ranking heuristic based on multi-method evidence. Not a probability metric or confirmed reserve volume."
            },
            "features": features
        }

        return self._real_prospectivity_geojson

    def load_real_mineralization_evidence_geojson(self, mine_id: str = "MOIL_BALAGHAT") -> Dict[str, Any]:
        """
        Loads authoritative mineralization & site evidence with spatial coordinate support.
        """
        norm_id = mine_id.strip().upper()
        if norm_id != "MOIL_BALAGHAT":
            return {
                "type": "FeatureCollection",
                "metadata": {
                    "mine_id": mine_id,
                    "is_available": False,
                    "data_status": "unavailable"
                },
                "features": []
            }

        if self._real_mineralization_evidence_geojson is not None:
            return self._real_mineralization_evidence_geojson

        evid_csv = settings.REAL_DATA_DIR / "geology" / "balaghat" / "mineralization_evidence.csv"
        if not evid_csv.exists():
            raise FileNotFoundError(f"Mineralization evidence CSV not found at {evid_csv}")

        df = pd.read_csv(evid_csv)
        features = []

        min_lon, max_lon = 80.2038, 80.2525
        min_lat, max_lat = 21.8241, 21.8688

        for _, row in df.iterrows():
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            coord_type = str(row["coordinate_type"])
            precision = str(row["coordinate_precision"])

            in_aoi = (min_lon <= lon <= max_lon) and (min_lat <= lat <= max_lat)

            evid_id = str(row["evidence_id"])
            if evid_id == "EVID_MOIL_BALAGHAT_BHARWELI_01":
                role = "Primary similarity anchor (GRID-13860)"
                category = "verified_shaft_anchor"
            elif evid_id == "EVID_GSI_BHARWELI_OUTCROP_02":
                role = "Direct geological occurrence context (Mansar Reef)"
                category = "verified_outcrop_strike"
            else:
                role = "Regional belt occurrence evidence"
                category = "regional_evidence"

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [round(lon, 6), round(lat, 6)]
                },
                "properties": {
                    "evidence_id": evid_id,
                    "evidence_type": str(row["evidence_type"]),
                    "mine_or_occurrence_name": str(row["mine_or_occurrence_name"]),
                    "commodity": str(row["commodity"]),
                    "operator": str(row["operator"]),
                    "district": str(row["district"]),
                    "state": str(row["state"]),
                    "coordinate_type": coord_type,
                    "coordinate_precision": precision,
                    "source_organization": str(row["source_organization"]),
                    "source_title": str(row["source_title"]),
                    "source_url": str(row.get("source_url", "")),
                    "evidence_description": str(row["evidence_description"]),
                    "spatial_reliability": str(row["spatial_reliability"]),
                    "status": str(row["status"]),
                    "in_aoi": in_aoi,
                    "evidence_category": category,
                    "role_in_experiment": role,
                    "scientific_caveat": "Reference site evidence used for similarity benchmarking. Presence does not independently validate model ranking."
                }
            })

        self._real_mineralization_evidence_geojson = {
            "type": "FeatureCollection",
            "metadata": {
                "mine_id": "MOIL_BALAGHAT",
                "data_status": "real_authoritative",
                "count": len(features),
                "in_aoi_count": sum(1 for f in features if f["properties"]["in_aoi"]),
                "source": "IBM, GSI, MoEFCC PARIVESH, MOIL Statutory Disclosures"
            },
            "features": features
        }

        return self._real_mineralization_evidence_geojson

    # --- DSR 2022 Balaghat Source-Derived Access Methods ---

    def load_dsr_source_manifest(self) -> Dict[str, Any]:
        """Loads the machine-readable Balaghat DSR source manifest."""
        manifest_file = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "source_manifest.json"
        if not manifest_file.exists():
            raise FileNotFoundError(f"DSR source manifest not found at {manifest_file}")
        with open(manifest_file, "r", encoding="utf-8") as f:
            self._dsr_manifest = json.load(f)
        return self._dsr_manifest

    def load_dsr_mine_registry(self, mine_id: Optional[str] = None) -> pd.DataFrame:
        """Loads Balaghat DSR mine and lease registry."""
        if self._dsr_mines_df is None:
            csv_path = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "mine_registry.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"DSR mine registry not found at {csv_path}")
            df = pd.read_csv(csv_path)
            valid, errors = DataValidator.validate_dsr_mine_registry(df)
            if not valid:
                raise ValueError(f"DSR mine registry validation failed: {errors}")
            self._dsr_mines_df = df

        df = self._dsr_mines_df.copy()
        if mine_id:
            norm_id = mine_id.strip().upper()
            df = df[
                (df["mine_id"].str.upper() == norm_id) |
                (df["mine_name"].str.upper().str.contains(norm_id))
            ]
        return df

    def load_dsr_lease_areas(self, mine_id: Optional[str] = None) -> pd.DataFrame:
        """Loads Balaghat DSR lease breakdown and clearance data."""
        if self._dsr_lease_areas_df is None:
            csv_path = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "lease_areas.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"DSR lease areas not found at {csv_path}")
            self._dsr_lease_areas_df = pd.read_csv(csv_path)

        df = self._dsr_lease_areas_df.copy()
        if mine_id:
            norm_id = mine_id.strip().upper()
            df = df[df["mine_id"].str.upper() == norm_id]
        return df

    def load_dsr_boundary_pillars(self, mine_id: Optional[str] = None) -> pd.DataFrame:
        """Loads Balaghat DSR surveyed boundary pillars."""
        if self._dsr_boundary_pillars_df is None:
            csv_path = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "boundary_pillars.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"DSR boundary pillars not found at {csv_path}")
            df = pd.read_csv(csv_path)
            valid, errors = DataValidator.validate_dsr_boundary_pillars(df)
            if not valid:
                raise ValueError(f"DSR boundary pillars validation failed: {errors}")
            self._dsr_boundary_pillars_df = df

        df = self._dsr_boundary_pillars_df.copy()
        if mine_id:
            norm_id = mine_id.strip().upper()
            df = df[df["mine_id"].str.upper() == norm_id]
        return df

    def load_dsr_boundaries_geojson(self, mine_id: Optional[str] = None) -> Dict[str, Any]:
        """Loads Balaghat DSR validated lease boundaries and pillar GeoJSON."""
        if self._dsr_boundaries_geojson is None:
            geojson_path = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "boundaries.geojson"
            if not geojson_path.exists():
                raise FileNotFoundError(f"DSR boundaries GeoJSON not found at {geojson_path}")
            with open(geojson_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            valid, errors = DataValidator.validate_dsr_boundaries_geojson(data)
            if not valid:
                raise ValueError(f"DSR boundaries GeoJSON validation failed: {errors}")
            self._dsr_boundaries_geojson = data

        if not mine_id:
            return self._dsr_boundaries_geojson

        norm_id = mine_id.strip().upper()
        features = [
            f for f in self._dsr_boundaries_geojson.get("features", [])
            if f.get("properties", {}).get("mine_id", "").upper() == norm_id
        ]
        return {
            "type": "FeatureCollection",
            "metadata": {
                **self._dsr_boundaries_geojson.get("metadata", {}),
                "filter_mine_id": mine_id,
                "count": len(features)
            },
            "features": features
        }

    def load_dsr_geology_reference(self, formation_id: Optional[str] = None) -> pd.DataFrame:
        """Loads Sausar Group stratigraphic and ore bed reference data."""
        if self._dsr_geology_df is None:
            csv_path = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "geology_reference.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"DSR geology reference not found at {csv_path}")
            df = pd.read_csv(csv_path)
            valid, errors = DataValidator.validate_dsr_geology_reference(df)
            if not valid:
                raise ValueError(f"DSR geology reference validation failed: {errors}")
            self._dsr_geology_df = df

        df = self._dsr_geology_df.copy()
        if formation_id:
            norm_id = formation_id.strip().upper()
            df = df[df["formation_id"].str.upper() == norm_id]
        return df

    def load_dsr_grade_reference(self, mine_id: Optional[str] = None) -> pd.DataFrame:
        """Loads manganese grade and assay distribution reference."""
        if self._dsr_grade_df is None:
            csv_path = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "grade_reference.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"DSR grade reference not found at {csv_path}")
            df = pd.read_csv(csv_path)
            valid, errors = DataValidator.validate_dsr_grade_reference(df)
            if not valid:
                raise ValueError(f"DSR grade reference validation failed: {errors}")
            self._dsr_grade_df = df

        df = self._dsr_grade_df.copy()
        if mine_id:
            norm_id = mine_id.strip().upper()
            df = df[df["mine_id"].str.upper() == norm_id]
        return df

    def load_dsr_exploration_evidence(self, mine_id: Optional[str] = None) -> pd.DataFrame:
        """Loads aggregate exploration drilling and UNFC reserve evidence."""
        if self._dsr_exploration_df is None:
            csv_path = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "exploration_evidence.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"DSR exploration evidence not found at {csv_path}")
            self._dsr_exploration_df = pd.read_csv(csv_path)

        df = self._dsr_exploration_df.copy()
        if mine_id:
            norm_id = mine_id.strip().upper()
            df = df[df["mine_id"].str.upper() == norm_id]
        return df

    def load_dsr_production_reference(
        self,
        mine_id: Optional[str] = None,
        reporting_level: Optional[str] = None
    ) -> pd.DataFrame:
        """Loads Balaghat district and mine-level reported historical production."""
        if self._dsr_production_df is None:
            csv_path = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "production_reference.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"DSR production reference not found at {csv_path}")
            df = pd.read_csv(csv_path)
            valid, errors = DataValidator.validate_dsr_production_reference(df)
            if not valid:
                raise ValueError(f"DSR production reference validation failed: {errors}")
            self._dsr_production_df = df

        df = self._dsr_production_df.copy()
        if mine_id:
            norm_id = mine_id.strip().upper()
            df = df[df["mine_id"].str.upper() == norm_id]
        if reporting_level:
            df = df[df["reporting_level"].str.lower() == reporting_level.lower()]
        return df

    def load_dsr_mine_plan_targets(self, mine_id: Optional[str] = None) -> pd.DataFrame:
        """Loads approved mine-plan and EC production targets."""
        if self._dsr_mine_plan_df is None:
            csv_path = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "mine_plan_targets.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"DSR mine plan targets not found at {csv_path}")
            self._dsr_mine_plan_df = pd.read_csv(csv_path)

        df = self._dsr_mine_plan_df.copy()
        if mine_id:
            norm_id = mine_id.strip().upper()
            df = df[df["mine_id"].str.upper() == norm_id]
        return df

    def load_dsr_constraints(self, mine_id: Optional[str] = None) -> pd.DataFrame:
        """Loads mining, geotechnical, and environmental constraints."""
        if self._dsr_constraints_df is None:
            csv_path = settings.REAL_DATA_DIR / "dsr" / "balaghat" / "constraints.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"DSR constraints not found at {csv_path}")
            df = pd.read_csv(csv_path)
            valid, errors = DataValidator.validate_dsr_constraints(df)
            if not valid:
                raise ValueError(f"DSR constraints validation failed: {errors}")
            self._dsr_constraints_df = df

        df = self._dsr_constraints_df.copy()
        if mine_id:
            norm_id = mine_id.strip().upper()
            df = df[df["mine_id"].str.upper() == norm_id]
        return df


# Global singleton loader instance
data_loader = DataLoader()
