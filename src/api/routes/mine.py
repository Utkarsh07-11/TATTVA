"""Mine operations overview, block polygons, and fleet telemetry."""

from typing import Dict, Any
from fastapi import APIRouter, Query

from config.settings import settings
from src.api.deps import BLOCK_META, compute_forecast_payload
from src.api.schemas import MineOverviewResponse, BlockSummary
from src.data.loader import data_loader

router = APIRouter(prefix="/mine", tags=["Mine Operations & Management"])


@router.get("/overview", response_model=MineOverviewResponse)
def get_mine_overview(selected_block: str = Query("BLOCK_A")) -> MineOverviewResponse:
    prod_df = data_loader.load_production_data()
    eq_df = data_loader.load_equipment_events()

    block_summaries = []
    total_target = 0.0
    total_forecast = 0.0
    total_actual = 0.0

    for b in BLOCK_META:
        b_id = b["id"]
        b_prod = prod_df[prod_df["mine_block_id"] == b_id]
        last_30_actual = float(b_prod.iloc[-30:]["actual_tonnes"].sum()) if len(b_prod) >= 30 else float(b_prod["actual_tonnes"].sum()) if len(b_prod) else 0.0

        forecast = compute_forecast_payload(b_id, horizon_days=30)
        block_summaries.append(BlockSummary(
            block_id=b_id,
            name=b["name"],
            status=b["status"],
            current_month_actual=round(last_30_actual, 1),
            target_tonnes=b["target"],
            forecast_tonnes=forecast["forecast_tonnes"],
            shortfall_probability=forecast["shortfall_probability"],
            risk_level=forecast["risk_level"],
        ))
        total_target += b["target"]
        total_forecast += forecast["forecast_tonnes"]
        total_actual += last_30_actual

    latest_events = eq_df.sort_values("start_time").groupby("equipment_id").last()
    under_repair = int((latest_events["event_type"].isin(["downtime", "repair"])).sum())
    active_count = max(0, len(latest_events) - under_repair)
    selected_summary = next((bs for bs in block_summaries if bs.block_id == selected_block), block_summaries[0])

    return MineOverviewResponse(
        mine_id="MOIL_BALAGHAT_01",
        mine_name="MOIL Central Manganese Mine (Balaghat Complex)",
        selected_block=selected_block,
        total_monthly_target=total_target,
        total_monthly_actual=round(total_actual, 1),
        total_monthly_forecast=round(total_forecast, 1),
        aggregate_risk_level=selected_summary.risk_level,
        blocks=block_summaries,
        active_equipment_count=active_count,
        equipment_under_repair_count=under_repair,
        current_weather={
            "condition": "Scattered Rain / Monsoon Showers",
            "forecast_rain_next_7d_mm": 42.5,
            "soil_moisture_index": "High",
            "blast_risk_advisory": "Yellow Alert: Reschedule bench blasts to dry shift",
        },
        model_status={
            "forecasting_model": "LightGBM Quantile Regressor (P10, P50, P90)",
            "prospectivity_model": "XGBoost Classifier (Spatial Block CV)",
            "explainability_engine": "SHAP TreeExplainer",
            "decision_optimizer": "PuLP Constrained Mixed-Integer Linear Program",
            "status": "HEALTHY_AND_VERIFIED",
        },
        synthetic_watermark=True,
    )


@router.get("/blocks")
def get_mine_blocks_geojson() -> Dict[str, Any]:
    return data_loader.load_mine_blocks_geojson()


@router.get("/equipment")
def get_equipment_status() -> Dict[str, Any]:
    clat = settings.CENTER_LAT
    clon = settings.CENTER_LON
    fleet = [
        {"id": "EXC-01", "type": "Excavator 120T", "block": "BLOCK_A", "lat": clat + 0.003, "lon": clon - 0.002, "status": "OPERATIONAL", "health_pct": 92},
        {"id": "EXC-02", "type": "Excavator 85T", "block": "BLOCK_A", "lat": clat + 0.004, "lon": clon + 0.001, "status": "OPERATIONAL", "health_pct": 88},
        {"id": "EXC-03", "type": "Excavator 85T", "block": "BLOCK_A", "lat": clat + 0.001, "lon": clon - 0.003, "status": "UNDER_MAINTENANCE", "health_pct": 54},
        {"id": "EXC-04", "type": "Excavator 120T", "block": "BLOCK_B", "lat": clat + 0.007, "lon": clon + 0.008, "status": "STANDBY", "health_pct": 96},
        {"id": "EXC-05", "type": "Excavator 85T", "block": "BLOCK_B", "lat": clat + 0.009, "lon": clon + 0.010, "status": "OPERATIONAL", "health_pct": 85},
        {"id": "EXC-06", "type": "Excavator 85T", "block": "BLOCK_C", "lat": clat - 0.007, "lon": clon - 0.008, "status": "OPERATIONAL", "health_pct": 79},
        {"id": "DRL-01", "type": "Rotary Drill 150mm", "block": "BLOCK_A", "lat": clat + 0.005, "lon": clon - 0.001, "status": "OPERATIONAL", "health_pct": 91},
        {"id": "DRL-03", "type": "Rotary Drill 150mm", "block": "BLOCK_B", "lat": clat + 0.008, "lon": clon + 0.006, "status": "OPERATIONAL", "health_pct": 87},
    ]
    return {"fleet": fleet, "total_units": len(fleet), "synthetic": True}
