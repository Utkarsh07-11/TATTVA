"""
Real Data Service API Endpoints for TATTVA
Exposes authoritative MOIL statutory mines, historical reported production,
verified satellite/DEM raster layer metadata, and Balaghat District Survey Report (DSR 2022) datasets.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.data.loader import data_loader
from src.data.registry import real_data_registry
from src.api.deps import compute_production_reconciliation_payload

router = APIRouter(prefix="/real", tags=["Authoritative Real Data Services"])


class ProductionReconciliationRequest(BaseModel):
    mine_block_id: str = Field(default="Block_A", description="Target mine block ID (Block_A, Block_B, Block_C)")
    horizon_days: int = Field(default=30, ge=7, le=90, description="Simulation horizon in days")
    custom_target: Optional[float] = Field(default=None, description="Custom operational target in tonnes")
    equipment_availability_pct: Optional[float] = Field(default=None, ge=40.0, le=100.0, description="Scenario equipment availability %")
    blasting_delay_flag: Optional[int] = Field(default=None, ge=0, le=1, description="Scenario blasting delay flag (0 or 1)")
    rainfall_mm: Optional[float] = Field(default=None, ge=0.0, le=300.0, description="Scenario rainfall in mm")


def _resolve_mine_or_404(mine_id: str) -> str:
    """Helper to validate mine_id against MOIL and DSR registries, returning canonical ID or raising 404."""
    norm_id = mine_id.strip().upper()
    try:
        moil_df = data_loader.load_real_mines_df()
        moil_match = moil_df[
            (moil_df["mine_id"].str.upper() == norm_id) |
            (moil_df["mine_name"].str.upper() == norm_id)
        ]
        if not moil_match.empty:
            return str(moil_match.iloc[0]["mine_id"])
    except Exception:
        pass

    try:
        dsr_df = data_loader.load_dsr_mine_registry()
        dsr_match = dsr_df[
            (dsr_df["mine_id"].str.upper() == norm_id) |
            (dsr_df["mine_name"].str.upper().str.contains(norm_id))
        ]
        if not dsr_match.empty:
            return str(dsr_match.iloc[0]["mine_id"])
    except Exception:
        pass

    raise HTTPException(
        status_code=404,
        detail=f"Mine '{mine_id}' not found in the audited MOIL or Balaghat DSR registry."
    )


@router.get("/mines")
def get_real_mines() -> Dict[str, Any]:
    """Returns the audited 10-mine MOIL statutory registry."""
    df = data_loader.load_real_mines_df()
    mines = []
    for _, row in df.iterrows():
        mines.append({
            "mine_id": str(row["mine_id"]),
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
            "data_status": "real"
        })
    return {
        "count": len(mines),
        "data_status": "real",
        "mines": mines
    }


@router.get("/mine-dashboard/{mine_id}")
def get_real_mine_dashboard(mine_id: str) -> Dict[str, Any]:
    """Returns consolidated metadata, provenance, and 5-category Data Availability Status for a mine."""
    summary = data_loader.get_mine_dashboard_summary(mine_id)
    if not summary.get("exists", False):
        raise HTTPException(
            status_code=404,
            detail=f"Mine '{mine_id}' not found in the audited MOIL statutory registry."
        )
    return summary


@router.get("/mines/{mine_id}")
def get_real_mine_detail(mine_id: str) -> Dict[str, Any]:
    """Returns detailed information and layer availability for a specific MOIL mine."""
    info = data_loader.get_mine_layer_availability(mine_id)
    if not info.get("exists", False):
        raise HTTPException(
            status_code=404,
            detail=f"Mine '{mine_id}' not found in the audited MOIL statutory registry."
        )
    return info


@router.get("/mines/{mine_id}/layers")
def get_real_mine_layers(mine_id: str) -> Dict[str, Any]:
    """Returns the geospatial layer availability map for a specific mine."""
    info = data_loader.get_mine_layer_availability(mine_id)
    if not info.get("exists", False):
        raise HTTPException(
            status_code=404,
            detail=f"Mine '{mine_id}' not found in the audited MOIL statutory registry."
        )
    return {
        "mine_id": info["mine_id"],
        "mine_name": info["mine_name"],
        "layers": info["layers"],
        "data_status": "real"
    }


@router.get("/production")
def get_real_production(
    period: Optional[str] = Query(None, description="Filter by reporting period, e.g. FY2023-24, Q3_FY2025-26, 2025-08"),
    period_type: Optional[str] = Query(None, description="Filter by grain: annual, quarterly, monthly"),
    company: Optional[str] = Query(None, description="Filter by operating company, e.g. MOIL Limited"),
    state: Optional[str] = Query(None, description="Filter by state, e.g. MP_AND_MAH, Madhya Pradesh"),
    commodity: Optional[str] = Query(None, description="Filter by mineral commodity, e.g. Manganese Ore")
) -> Dict[str, Any]:
    """Returns reported historical manganese production with optional filtering."""
    df = data_loader.load_real_production_df(
        period=period,
        period_type=period_type,
        company=company,
        state=state,
        commodity=commodity
    )
    records = []
    for _, row in df.iterrows():
        records.append({
            "period": str(row["period"]),
            "period_type": str(row["period_type"]),
            "mine": str(row["mine"]),
            "company": str(row["company"]),
            "state": str(row["state"]),
            "commodity": str(row["commodity"]),
            "production_tonnes": float(row["production_tonnes"]),
            "grade_percent": float(row["grade_percent"]) if pd.notna(row.get("grade_percent")) and str(row.get("grade_percent")).strip() != "" else None,
            "source": str(row["source"]),
            "source_page": str(row["source_page"]),
            "source_table": str(row["source_table"]),
            "data_status": str(row["data_status"])
        })
    return {
        "count": len(records),
        "data_status": "real",
        "records": records
    }


@router.get("/rasters/summary")
def get_real_rasters_summary() -> Dict[str, Any]:
    """Returns lightweight metadata for all available real and derived raster datasets."""
    descriptors = real_data_registry.list_descriptors()
    rasters = []
    for desc in descriptors:
        if desc.dataset_type in ("raster_cog", "raster_geotiff") and desc.is_available:
            meta = real_data_registry.get_raster_metadata(desc.dataset_id)
            if meta:
                rasters.append(meta)

    return {
        "count": len(rasters),
        "rasters": rasters
    }


@router.get("/prospectivity/{mine_id}")
def get_real_prospectivity_meta(mine_id: str) -> Dict[str, Any]:
    """
    Returns the Phase 9B real prospectivity experiment metadata, score distributions,
    cluster statistics, provenance, and scientific limitations for a specific mine.
    """
    norm_id = mine_id.strip().upper()
    try:
        data = data_loader.load_real_prospectivity_meta(norm_id)
        return data
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Real prospectivity experiment data not found: {str(e)}"
        )


@router.get("/prospectivity/{mine_id}/geojson")
def get_real_prospectivity_geojson(mine_id: str) -> Dict[str, Any]:
    """
    Returns the GeoJSON FeatureCollection of 27,720 30m grid polygon cells with
    Phase 9B exploration priority, anomaly, robust distance, and anchor similarity scores.
    """
    norm_id = mine_id.strip().upper()
    try:
        geojson = data_loader.load_real_prospectivity_geojson(norm_id)
        return geojson
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Real prospectivity GeoJSON not found: {str(e)}"
        )


@router.get("/prospectivity/{mine_id}/evidence")
def get_real_mineralization_evidence(mine_id: str) -> Dict[str, Any]:
    """
    Returns the authoritative mineralization and site evidence points for the mine AOI.
    """
    norm_id = mine_id.strip().upper()
    try:
        evidence = data_loader.load_real_mineralization_evidence_geojson(norm_id)
        return evidence
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Real mineralization evidence not found: {str(e)}"
        )


@router.get("/production/reconciliation")
def get_production_reconciliation(
    mine_block_id: str = Query("Block_A", description="Target mine block ID (Block_A, Block_B, Block_C)"),
    horizon_days: int = Query(30, ge=7, le=90, description="Simulation horizon in days"),
    target_tonnes: Optional[float] = Query(None, description="Explicit operational target in tonnes"),
    equipment_availability_pct: Optional[float] = Query(None, ge=40.0, le=100.0, description="Scenario override for equipment availability %"),
    blasting_delay_flag: Optional[int] = Query(None, ge=0, le=1, description="Scenario override for blasting delay flag (0 or 1)"),
    rainfall_mm: Optional[float] = Query(None, ge=0.0, le=300.0, description="Scenario override for rainfall in mm")
) -> Dict[str, Any]:
    """
    Returns unified Phase 12 Production Intelligence & Reconciliation payload.
    Features strict separation between MOIL Company-Level Reported Historical Production (Macro)
    and TATTVA Block-Level Operational Simulation (Micro).
    """
    return compute_production_reconciliation_payload(
        mine_block_id=mine_block_id,
        horizon_days=horizon_days,
        custom_target=target_tonnes,
        equipment_availability_pct=equipment_availability_pct,
        blasting_delay_flag=blasting_delay_flag,
        rainfall_mm=rainfall_mm,
    )


@router.post("/production/reconciliation")
def post_production_reconciliation(
    req: ProductionReconciliationRequest
) -> Dict[str, Any]:
    """
    POST endpoint for interactive scenario-adjusted production reconciliation and sandbox analysis.
    """
    return compute_production_reconciliation_payload(
        mine_block_id=req.mine_block_id,
        horizon_days=req.horizon_days,
        custom_target=req.custom_target,
        equipment_availability_pct=req.equipment_availability_pct,
        blasting_delay_flag=req.blasting_delay_flag,
        rainfall_mm=req.rainfall_mm,
    )


# --- Balaghat District Survey Report (DSR 2022) Endpoints ---

@router.get("/dsr")
def get_dsr_manifest() -> Dict[str, Any]:
    """Returns the comprehensive Balaghat DSR 2022 source manifest and dataset catalogue."""
    try:
        manifest = data_loader.load_dsr_source_manifest()
        return manifest
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load DSR manifest: {str(e)}")


@router.get("/dsr/mines")
def get_dsr_mines(
    mine_id: Optional[str] = Query(None, description="Optional mine_id filter (e.g. MOIL_BALAGHAT, MOIL_UKWA)"),
    tehsil: Optional[str] = Query(None, description="Optional tehsil filter (e.g. Balaghat, Baihar, Katangi)")
) -> Dict[str, Any]:
    """Returns the source-derived Balaghat DSR manganese mine and lease registry."""
    df = data_loader.load_dsr_mine_registry(mine_id=mine_id)
    if tehsil:
        df = df[df["tehsil"].str.lower().str.contains(tehsil.lower())]

    records = df.to_dict(orient="records")
    return {
        "count": len(records),
        "data_status": "source-derived",
        "provenance_status": "verified",
        "source": "Balaghat District Survey Report 2022",
        "mines": records
    }


@router.get("/dsr/{mine_id}")
def get_dsr_mine_profile(mine_id: str) -> Dict[str, Any]:
    """Returns consolidated DSR profile (lease info, clearances, geology, grade, production, constraints) for a mine."""
    canon_id = _resolve_mine_or_404(mine_id)
    mines_df = data_loader.load_dsr_mine_registry(mine_id=canon_id)
    if mines_df.empty:
        raise HTTPException(status_code=404, detail=f"Mine '{mine_id}' not found in DSR mine registry.")

    mine_info = mines_df.iloc[0].to_dict()
    lease_df = data_loader.load_dsr_lease_areas(mine_id=canon_id)
    grade_df = data_loader.load_dsr_grade_reference(mine_id=canon_id)
    prod_df = data_loader.load_dsr_production_reference(mine_id=canon_id)
    plan_df = data_loader.load_dsr_mine_plan_targets(mine_id=canon_id)
    con_df = data_loader.load_dsr_constraints(mine_id=canon_id)
    exp_df = data_loader.load_dsr_exploration_evidence(mine_id=canon_id)

    return {
        "mine_id": canon_id,
        "data_status": "source-derived",
        "provenance_status": "verified",
        "source": "Balaghat District Survey Report 2022",
        "general_info": mine_info,
        "lease_areas": lease_df.to_dict(orient="records"),
        "grade_reference": grade_df.to_dict(orient="records"),
        "exploration_evidence": exp_df.to_dict(orient="records"),
        "production_history": prod_df.to_dict(orient="records"),
        "mine_plan_targets": plan_df.to_dict(orient="records"),
        "constraints": con_df.to_dict(orient="records")
    }


@router.get("/dsr/{mine_id}/boundaries")
def get_dsr_mine_boundaries(mine_id: str) -> Dict[str, Any]:
    """Returns validated statutory reference points and boundary metadata for a mine."""
    canon_id = _resolve_mine_or_404(mine_id)
    geojson_data = data_loader.load_dsr_boundaries_geojson(mine_id=canon_id)
    pillars_df = data_loader.load_dsr_boundary_pillars(mine_id=canon_id)

    return {
        "mine_id": canon_id,
        "data_status": "source-derived",
        "provenance_status": "verified",
        "polygon_geometry_status": "unavailable",
        "point_geometry_status": "available",
        "source": "Balaghat District Survey Report 2022 & IBM MCDR Mining Plans",
        "boundary_geojson": geojson_data,
        "boundary_pillars": pillars_df.to_dict(orient="records")
    }


@router.get("/dsr/{mine_id}/geology")
def get_dsr_mine_geology(mine_id: str) -> Dict[str, Any]:
    """Returns Sausar Group stratigraphic context and manganese ore bed descriptions for a mine."""
    canon_id = _resolve_mine_or_404(mine_id)
    df = data_loader.load_dsr_geology_reference()
    # Filter formations that list this mine or return the full regional stratigraphy
    relevant = df[df["representative_mines"].str.contains(canon_id, na=False)]
    return {
        "mine_id": canon_id,
        "data_status": "source-derived",
        "provenance_status": "verified",
        "source": "Balaghat District Survey Report 2022 & GSI Bulletin Series A No. 22",
        "formation_count": len(df),
        "directly_associated_formations": relevant.to_dict(orient="records"),
        "regional_stratigraphy": df.to_dict(orient="records")
    }


@router.get("/dsr/{mine_id}/grade")
def get_dsr_mine_grade(mine_id: str) -> Dict[str, Any]:
    """Returns chemical grade distributions (% Mn, % Fe, % SiO2, % P) by ore type for a mine."""
    canon_id = _resolve_mine_or_404(mine_id)
    df = data_loader.load_dsr_grade_reference(mine_id=canon_id)
    return {
        "mine_id": canon_id,
        "data_status": "source-derived",
        "provenance_status": "verified",
        "source": "Balaghat District Survey Report 2022 & MOIL Product Specifications",
        "count": len(df),
        "grades": df.to_dict(orient="records")
    }


@router.get("/dsr/{mine_id}/exploration")
def get_dsr_mine_exploration(mine_id: str) -> Dict[str, Any]:
    """Returns aggregate exploration drilling, meterage, and UNFC reserve estimates for a mine."""
    canon_id = _resolve_mine_or_404(mine_id)
    df = data_loader.load_dsr_exploration_evidence(mine_id=canon_id)
    return {
        "mine_id": canon_id,
        "data_status": "source-derived",
        "provenance_status": "verified",
        "source": "Balaghat District Survey Report 2022 & IBM MCDR Mining Plans",
        "count": len(df),
        "exploration_evidence": df.to_dict(orient="records")
    }


@router.get("/dsr/{mine_id}/production")
def get_dsr_mine_production(mine_id: str) -> Dict[str, Any]:
    """Returns reported historical production and approved planned targets for a mine."""
    canon_id = _resolve_mine_or_404(mine_id)
    hist_df = data_loader.load_dsr_production_reference(mine_id=canon_id)
    plan_df = data_loader.load_dsr_mine_plan_targets(mine_id=canon_id)

    return {
        "mine_id": canon_id,
        "data_status": "source-derived",
        "provenance_status": "verified",
        "source": "Balaghat District Survey Report 2022 & IBM Mining Plans",
        "reported_history": hist_df.to_dict(orient="records"),
        "planned_targets": plan_df.to_dict(orient="records")
    }


@router.get("/dsr/{mine_id}/constraints")
def get_dsr_mine_constraints(mine_id: str) -> Dict[str, Any]:
    """Returns mining, environmental, and operational constraints for a mine."""
    canon_id = _resolve_mine_or_404(mine_id)
    df = data_loader.load_dsr_constraints(mine_id=canon_id)
    return {
        "mine_id": canon_id,
        "data_status": "source-derived",
        "provenance_status": "verified",
        "source": "Balaghat District Survey Report 2022 & MoEFCC EC Clearances",
        "count": len(df),
        "constraints": df.to_dict(orient="records")
    }


@router.get("/dsr/{mine_id}/context")
def get_dsr_mine_context(mine_id: str) -> Dict[str, Any]:
    """
    Returns consolidated contextual geological stratigraphy, grade distributions, and leasehold
    area breakdowns for a mine. Maintained strictly as source-derived reference data.
    """
    canon_id = _resolve_mine_or_404(mine_id)
    mines_df = data_loader.load_dsr_mine_registry(mine_id=canon_id)
    lease_df = data_loader.load_dsr_lease_areas(mine_id=canon_id)
    geol_df = data_loader.load_dsr_geology_reference()
    grade_df = data_loader.load_dsr_grade_reference(mine_id=canon_id)

    mine_info = mines_df.iloc[0].to_dict() if not mines_df.empty else {}
    associated_geology = geol_df[geol_df["representative_mines"].str.contains(canon_id, na=False)]

    return {
        "mine_id": canon_id,
        "data_classification": "SOURCE-DERIVED / PARTIAL",
        "provenance_status": "verified",
        "scope": "mine_level_contextual_reference",
        "spatial_status": "non_spatial_tabular_reference",
        "geometry_status": "unavailable",
        "source": "Balaghat District Survey Report 2022 & GSI Bulletin Series A No. 22",
        "disclaimer": "Contextual geological stratigraphy and chemical grade distributions. Textual/tabular reference only; not digital vector GIS polygons.",
        "general_info": mine_info,
        "lease_areas": lease_df.to_dict(orient="records"),
        "directly_associated_formations": associated_geology.to_dict(orient="records"),
        "grade_distributions": grade_df.to_dict(orient="records")
    }


@router.get("/dsr/{mine_id}/evidence")
def get_dsr_mine_evidence(mine_id: str) -> Dict[str, Any]:
    """
    Returns documented aggregate exploration drilling evidence, UNFC reserve estimates,
    and verified regional mineralization anchors for a mine.
    """
    canon_id = _resolve_mine_or_404(mine_id)
    exp_df = data_loader.load_dsr_exploration_evidence(mine_id=canon_id)
    try:
        min_evid = data_loader.load_real_mineralization_evidence_geojson(mine_id=canon_id)
    except Exception:
        min_evid = {"type": "FeatureCollection", "features": []}

    return {
        "mine_id": canon_id,
        "data_classification": "SOURCE-DERIVED",
        "provenance_status": "verified",
        "scope": "aggregate_exploration_evidence",
        "spatial_status": "aggregate_lease_and_regional_points",
        "source": "Balaghat District Survey Report 2022, IBM MCDR Mining Plans & GSI Memoirs",
        "disclaimer": "Documented aggregate borehole counts, meterage, and UNFC reserves. Not individual drillhole collar coordinates or downhole assay intervals.",
        "exploration_drilling_summary": exp_df.to_dict(orient="records"),
        "mineralization_evidence": min_evid
    }


@router.get("/capability-matrix")
def get_capability_matrix() -> Dict[str, Any]:
    """
    Returns the audited 10-mine dynamic capability matrix and tier classifications (Phase 18).
    Evaluates dimension-level capabilities dynamically from underlying data assets without hardcoded assumptions.
    """
    return data_loader.get_mine_capability_matrix()


@router.get("/decision/{mine_id}")
def get_real_decision_workflow(
    mine_id: str,
    horizon_days: int = Query(30, ge=7, le=90, description="Planning/simulation horizon in days"),
    custom_target: Optional[float] = Query(None, description="Custom operational target in tonnes"),
    equipment_availability_pct: Optional[float] = Query(None, ge=40.0, le=100.0, description="Scenario equipment availability %"),
    blasting_delay_flag: Optional[int] = Query(None, ge=0, le=1, description="Scenario blasting delay flag (0 or 1)"),
    rainfall_mm: Optional[float] = Query(None, ge=0.0, le=300.0, description="Scenario rainfall in mm"),
) -> Dict[str, Any]:
    """
    Unified End-to-End Decision Intelligence Workflow Endpoint (Phase 17 & Phase 18).
    Executes the coherent decision chain:
    DATA -> CONTEXT -> ANALYSIS -> EXPLANATION -> SCENARIO -> OPTIMIZATION -> RECOMMENDED ACTION -> LIMITATIONS
    Enforces strict dimension-level capability isolation (Level A/B/C/D).
    Non-simulated mines strictly return UNAVAILABLE_FOR_MINE for operational forecasting, SHAP, and optimization.
    """
    canon_id = _resolve_mine_or_404(mine_id)
    mines_df = data_loader.load_real_mines_df()
    mine_row = mines_df[mines_df["mine_id"] == canon_id]
    if mine_row.empty:
        raise HTTPException(status_code=404, detail=f"Mine '{mine_id}' not found in registry.")
    
    m_info = mine_row.iloc[0].to_dict()
    is_balaghat_mine = (canon_id == "MOIL_BALAGHAT")
    is_balaghat_district = (str(m_info.get("district", "")).lower() == "balaghat")

    # Layer & Constraint presence
    layer_info = data_loader.get_mine_layer_availability(canon_id)
    layers = layer_info.get("layers", {})
    try:
        c_df = data_loader.load_dsr_constraints(mine_id=canon_id)
        has_constraints = not c_df.empty
        has_operational_constraints = not c_df[c_df["constraint_category"] != "environmental"].empty
    except Exception:
        has_constraints = False
        has_operational_constraints = False

    # Tier derivation
    if is_balaghat_mine:
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

    # 1. MINE CONTEXT
    dsr_mine_df = data_loader.load_dsr_mine_registry(mine_id=canon_id) if is_balaghat_district else pd.DataFrame()
    dsr_info = dsr_mine_df.iloc[0].to_dict() if not dsr_mine_df.empty else {}
    
    lease_ha = float(dsr_info.get("lease_area_ha", m_info.get("lease_area_ha", 0.0))) if pd.notna(dsr_info.get("lease_area_ha", m_info.get("lease_area_ha"))) else None
    
    stage_1_context = {
        "mine_id": canon_id,
        "mine_name": str(m_info.get("mine_name")),
        "company": str(m_info.get("company")),
        "state": str(m_info.get("state")),
        "district": str(m_info.get("district")),
        "mineral": str(m_info.get("mineral")),
        "latitude": float(m_info.get("latitude")),
        "longitude": float(m_info.get("longitude")),
        "point_type": str(m_info.get("point_type", "mine_site_reference")),
        "lease_area_ha": lease_ha,
        "operating_status": str(dsr_info.get("operating_status", "Active")),
        "mining_method": str(dsr_info.get("mining_method", "Underground & Opencast" if is_balaghat_district else "Operating")),
        "source_citation": "MOIL Limited Statutory Disclosures & Balaghat DSR 2022" if is_balaghat_district else "MOIL Limited Statutory Disclosures",
        "data_classification": "REAL / SURVEYED & SOURCE-DERIVED" if is_balaghat_district else "REAL / SURVEYED"
    }

    # 2. DATA STATUS BREAKDOWN
    stage_2_status = {
        "remote_sensing_rasters": "AVAILABLE (Sentinel-2 L2A & Copernicus DEM 30m)" if is_balaghat_mine else "UNAVAILABLE_FOR_MINE",
        "dsr_stratigraphy_context": "AVAILABLE (Sausar Group Lithological Units)" if is_balaghat_district else "UNAVAILABLE_FOR_MINE",
        "dsr_exploration_evidence": "AVAILABLE (Aggregate Boreholes & UNFC Reserves)" if is_balaghat_district else "UNAVAILABLE_FOR_MINE",
        "dsr_statutory_constraints": "AVAILABLE (Recovery %, Stowing, Dewatering, EC Caps)" if has_constraints else "UNAVAILABLE_FOR_MINE",
        "cadastral_boundary_polygons": "UNAVAILABLE",
        "operational_simulation": "AVAILABLE (Synthetic shift operational simulation)" if is_balaghat_mine else "UNAVAILABLE_FOR_MINE",
        "drillhole_downhole_assays": "UNAVAILABLE (Real downhole assay logs remain confidential MOIL assets)"
    }

    # 3. OBSERVATIONS & FEATURES
    observations: Dict[str, Any] = {}
    if is_balaghat_mine:
        observations["operational_baseline_inputs"] = {
            "default_equipment_availability_pct": 82.5,
            "default_rainfall_mm": 0.0,
            "default_blasting_delay_flag": 0,
            "data_classification": "SIMULATION"
        }
    else:
        observations["operational_baseline_inputs"] = {
            "status": "UNAVAILABLE_FOR_MINE",
            "reason": "Operational shift simulation telemetry is calibrated only for Balaghat/Block A; not qualified for this mine."
        }

    if is_balaghat_district:
        try:
            geol_df = data_loader.load_dsr_geology_reference()
            assoc_geol = geol_df[geol_df["representative_mines"].str.contains(canon_id, na=False)]
            grade_df = data_loader.load_dsr_grade_reference(mine_id=canon_id)
            observations["geological_stratigraphy_reference"] = {
                "associated_formations": assoc_geol[["formation_name", "lithology_description", "manganese_ore_association"]].to_dict(orient="records"),
                "grade_distribution_ranges": grade_df[["grade_category", "mn_typical_pct", "fe_typical_pct", "sio2_typical_pct"]].to_dict(orient="records"),
                "data_classification": "SOURCE-DERIVED / PARTIAL"
            }
        except Exception:
            observations["geological_stratigraphy_reference"] = {"status": "UNAVAILABLE_FOR_MINE"}
    else:
        observations["geological_stratigraphy_reference"] = {
            "status": "UNAVAILABLE_FOR_MINE",
            "reason": "DSR regional geology reference is currently integrated for Balaghat district mines only."
        }

    # 4. ANALYTICAL SIGNAL (Exploration Priority + Production Forecast)
    analytical_signal: Dict[str, Any] = {}
    if is_balaghat_mine:
        try:
            meta = data_loader.load_real_prospectivity_meta(canon_id)
            analytical_signal["exploration_analytical_signal"] = {
                "signal_type": "RELATIVE_EXPLORATION_PRIORITY_RANKING",
                "model_ensemble": "Phase 9B Ensemble (Isolation Forest + PCA-Mahalanobis + Bharweli Anchor Similarity)",
                "summary_distributions": meta.get("summary_distributions", {}),
                "cluster_statistics": meta.get("cluster_statistics", []),
                "positive_anchors_count": meta.get("positive_anchors_count", 0),
                "data_classification": "EXPERIMENTAL",
                "disclaimer": "Relative exploration priority heuristic based on anomaly ensemble. Not a probability metric or confirmed reserve volume."
            }
        except Exception:
            analytical_signal["exploration_analytical_signal"] = {"status": "UNAVAILABLE_FOR_MINE"}
    else:
        analytical_signal["exploration_analytical_signal"] = {
            "status": "UNAVAILABLE_FOR_MINE",
            "reason": "Multi-spectral Sentinel-2 and DEM feature rasters currently processed for Balaghat district only."
        }

    # 5. OPERATIONAL SIMULATION, SHAP, SCENARIO, OPTIMIZATION (Strict Balaghat/Block A only)
    if is_balaghat_mine:
        target_block = "BLOCK_A"
        recon_payload = compute_production_reconciliation_payload(
            mine_block_id=target_block,
            horizon_days=horizon_days,
            custom_target=custom_target,
            equipment_availability_pct=equipment_availability_pct,
            blasting_delay_flag=blasting_delay_flag,
            rainfall_mm=rainfall_mm
        )

        micro_sim = recon_payload.get("micro_simulation", {})
        scen_recon = recon_payload.get("scenario_reconciliation", {})
        opt_options = recon_payload.get("optimizer_recommendations", [])

        target_val = float(micro_sim.get("operational_target_tonnes", 10000.0))
        base_forecast_val = float(micro_sim.get("baseline_forecast_tonnes", 8500.0))
        base_shortfall_val = float(micro_sim.get("baseline_shortfall_tonnes", 1500.0))

        analytical_signal["production_forecast_signal"] = {
            "signal_type": "QUANTILE_PRODUCTION_FORECAST",
            "model": "LightGBM Quantile Regressor (p10, p50, p90)",
            "horizon_days": horizon_days,
            "target_tonnes": target_val,
            "baseline_forecast_tonnes": base_forecast_val,
            "baseline_interval_90": micro_sim.get("baseline_interval_90"),
            "baseline_shortfall_tonnes": base_shortfall_val,
            "baseline_risk_level": micro_sim.get("baseline_risk_level"),
            "data_classification": "SIMULATION"
        }

        # SHAP Non-Causal Feature Attribution
        non_causal_contributors = []
        try:
            from src.api.deps import block_feature_frame, get_shap_engine
            _, feat_df = block_feature_frame(target_block)
            if feat_df is not None and not feat_df.empty:
                shap_engine = get_shap_engine()
                shap_res = shap_engine.explain_instance(
                    feat_df.iloc[-1:],
                    target_tonnes=target_val,
                    forecast_tonnes=base_forecast_val
                )
                for c in shap_res.get("contributors", []):
                    factor = c.get("factor", "")
                    pct = c.get("contribution_pct", 0.0)
                    impact = c.get("raw_impact_tonnes", 0.0)
                    if impact < 0:
                        association = f"{c.get('label', factor)} is associated with a lower model forecast in this scenario ({pct}% relative contribution)."
                    else:
                        association = f"{c.get('label', factor)} is associated with a higher model forecast in this scenario ({pct}% relative contribution)."
                    non_causal_contributors.append({
                        "factor": factor,
                        "label": c.get("label", factor),
                        "contribution_pct": pct,
                        "raw_impact_tonnes": impact,
                        "model_association": association,
                        "data_classification": "DERIVED_EXPLAINABILITY"
                    })
        except Exception:
            pass

        stage_5_explanation = {
            "explanation_method": "Tree-SHAP (Shapley Additive Explanations)",
            "target_tonnes": target_val,
            "forecast_tonnes": base_forecast_val,
            "expected_shortfall": base_shortfall_val,
            "associated_contributors": non_causal_contributors,
            "governance_note": "SHAP values represent model feature attribution under historical correlations, not proven mechanical causality.",
            "data_classification": "DERIVED_EXPLAINABILITY"
        }

        # Scenario
        has_overrides = scen_recon.get("has_scenario_overrides", False)
        scen_output = float(scen_recon.get("simulated_output_tonnes", base_forecast_val))
        scen_delta = float(scen_recon.get("scenario_variance_tonnes", 0.0))
        scen_shortfall = float(scen_recon.get("scenario_shortfall_tonnes", base_shortfall_val))

        stage_6_scenario = {
            "scenario_status": "SCENARIO_ADJUSTED" if has_overrides else "BASELINE_UNMODIFIED",
            "baseline_forecast_tonnes": base_forecast_val,
            "scenario_forecast_tonnes": scen_output,
            "delta_tonnes": scen_delta,
            "target_tonnes": target_val,
            "scenario_shortfall_tonnes": scen_shortfall,
            "scenario_risk_level": scen_recon.get("scenario_risk_level"),
            "applied_overrides": scen_recon.get("applied_parameters", {}),
            "data_classification": "SCENARIO-ADJUSTED OPERATIONAL SIMULATION"
        }

        # Optimization (PuLP MILP)
        recovery_gain = sum(opt.get("projected_recovery_tonnes", 0.0) for opt in opt_options[:2])
        residual_shortfall = max(0.0, round(scen_shortfall - recovery_gain, 1))

        stage_7_optimization = {
            "solver": "PuLP Mixed-Integer Linear Programming (MILP)",
            "solver_status": "Optimal" if opt_options else "Feasible",
            "objective": "Minimize production shortfall subject to equipment availability, budget, and operational constraints",
            "selected_actions": opt_options,
            "model_optimal_projected_recovery_tonnes": round(recovery_gain, 1),
            "residual_shortfall_tonnes": residual_shortfall,
            "solver_note": "Model-optimal action under the specified scenario and constraints. Not guaranteed production.",
            "data_classification": "OPTIMIZATION_MODEL_OUTPUT"
        }

        # Recommended Action
        statutory_constraints = []
        try:
            c_df = data_loader.load_dsr_constraints(mine_id=canon_id)
            statutory_constraints = c_df[["constraint_category", "constraint_name", "value", "unit", "source_name"]].to_dict(orient="records")
        except Exception:
            pass

        primary_action = opt_options[0] if opt_options else {
            "action_id": "ACT_MAINT_01",
            "action": "equipment_preventive_overhaul",
            "category": "maintenance",
            "title": "Preventive Maintenance Overhaul",
            "details": "Standard preventive maintenance schedule.",
            "expected_recovery_tonnes": 0.0,
            "cost": "Low",
            "feasibility": "High"
        }

        stage_8_recommendation = {
            "decision_type": "INTEGRATED_MINE_DECISION_SUPPORT",
            "mine_id": canon_id,
            "operational_status": "ACTION_RECOMMENDED" if opt_options else "MONITORING_SUFFICIENT",
            "primary_recommended_action": {
                "action_id": primary_action.get("action_id"),
                "action": primary_action.get("action", "operational_action"),
                "action_type": primary_action.get("category", primary_action.get("action", "operational_optimization")),
                "title": primary_action.get("title", ""),
                "description": primary_action.get("details", primary_action.get("description", "")),
                "projected_recovery_tonnes": primary_action.get("expected_recovery_tonnes", primary_action.get("projected_recovery_tonnes", 0.0)),
                "cost": primary_action.get("cost", "Moderate"),
                "feasibility": primary_action.get("feasibility", "High")
            },
            "all_ranked_actions": opt_options,
            "applicable_statutory_constraints": statutory_constraints,
            "exploration_guidance": "Focus exploratory soil/pXRF sampling on highest relative priority anomaly clusters (Score >= 0.70).",
            "data_classification": "RECOMMENDATION_LAYER"
        }

    else:
        # Non-Balaghat mines: Graceful degradation with UNAVAILABLE_FOR_MINE
        analytical_signal["production_forecast_signal"] = {
            "status": "UNAVAILABLE_FOR_MINE",
            "reason": "Operational shift simulation inputs do not exist for this mine. Sourced statutory historical production is available under /api/real/production."
        }

        stage_5_explanation = {
            "status": "UNAVAILABLE_FOR_MINE",
            "reason": "Tree-SHAP feature attribution requires operational model forecast."
        }

        stage_6_scenario = {
            "status": "UNAVAILABLE_FOR_MINE",
            "reason": "What-if scenario perturbation requires operational model baseline."
        }

        stage_7_optimization = {
            "status": "UNAVAILABLE_FOR_MINE",
            "reason": "PuLP MILP decision solver requires mine-specific simulation inputs, decision variables, and documented operational scope."
        }

        # Surface statutory constraints if available
        statutory_constraints = []
        if has_constraints:
            try:
                c_df = data_loader.load_dsr_constraints(mine_id=canon_id)
                statutory_constraints = c_df[["constraint_category", "constraint_name", "value", "unit", "source_name"]].to_dict(orient="records")
            except Exception:
                pass

        stage_8_recommendation = {
            "decision_type": "CONTEXTUAL_MINE_INTELLIGENCE",
            "mine_id": canon_id,
            "operational_status": "STATUTORY_MONITORING_ONLY",
            "applicable_statutory_constraints": statutory_constraints,
            "guidance_note": f"Operational dispatch optimization is UNAVAILABLE_FOR_MINE. Refer to statutory EC clearances and DSR guidelines for {m_info.get('mine_name')}." if has_constraints else f"Reference context only for {m_info.get('mine_name')}. No local operational constraints configured.",
            "data_classification": "SOURCE-DERIVED_CONTEXT" if has_constraints else "REGISTRY_REFERENCE"
        }

    # 9. PROVENANCE & LIMITATIONS
    stage_9_limitations = {
        "capability_tier": tier,
        "decision_workflow_status": workflow_status,
        "what_tattva_knows": [
            "Authoritative statutory mine registry metadata and coordinate point types (MOIL / IBM / DSR 2022).",
            "Reported company-level historical production series (FY16-FY24).",
            "Documented DSR regional geology stratigraphy, grade distribution spans, and aggregate borehole counts (where available).",
            "Statutory environmental clearance limits, recovery factors, and stowing ratios (where available)."
        ],
        "what_tattva_derives": [
            "30m Multi-spectral Sentinel-2 band indices (NDVI, Iron Oxide, Ferrous Iron, Clay Alteration) for Balaghat AOI.",
            "30m Copernicus DEM topographic indices (Elevation, Slope, Aspect, TPI) for Balaghat AOI.",
            "Tree-SHAP non-causal feature attribution rankings for operational variance (Balaghat only)."
        ],
        "what_tattva_simulates": [
            "Operational shift-level daily production logs and equipment availability (Balaghat Block A only).",
            "What-if scenario adjustments under user-specified parameters (Balaghat Block A only).",
            "PuLP MILP solver decision-space allocations (Balaghat Block A only)."
        ],
        "what_tattva_experimentally_ranks": [
            "Phase 9B relative exploration priority surface (Isolation Forest + PCA-Mahalanobis + Bharweli Anchor Similarity) for Balaghat AOI only."
        ],
        "what_is_unavailable_and_not_claimed": [
            "Surveyed closed-loop cadastral boundary polygons (pending statutory DGPS release).",
            "Proprietary downhole interval assay logs (retained as confidential MOIL assets).",
            "Real-time SCADA sensor telemetry (simulated in Digital Mine for Balaghat).",
            "Zero claims of geological certainty, statistical occurrence metrics, or autonomous decision-making."
        ],
        "data_classification_taxonomy": [
            "REAL / SURVEYED",
            "SOURCE-DERIVED",
            "SOURCE-DERIVED / PARTIAL",
            "DERIVED",
            "REFERENCE",
            "SIMULATION",
            "EXPERIMENTAL",
            "UNAVAILABLE",
            "UNAVAILABLE_FOR_MINE"
        ]
    }

    return {
        "mine_id": canon_id,
        "mine_name": str(m_info.get("mine_name")),
        "tier": tier,
        "decision_workflow_status": workflow_status,
        "decision_workflow": {
            "stage_1_mine_context": stage_1_context,
            "stage_2_data_status": stage_2_status,
            "stage_3_observations_and_features": observations,
            "stage_4_analytical_signal": analytical_signal,
            "stage_5_explanation": stage_5_explanation,
            "stage_6_scenario": stage_6_scenario,
            "stage_7_optimization": stage_7_optimization,
            "stage_8_recommended_action": stage_8_recommendation,
            "stage_9_provenance_and_limitations": stage_9_limitations
        }
    }


