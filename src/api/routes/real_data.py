"""
Real Data Service API Endpoints for TATTVA
Exposes authoritative MOIL statutory mines, historical reported production,
and verified satellite/DEM raster layer metadata.
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


