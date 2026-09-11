import json
import sys
from fastapi.testclient import TestClient
from src.api.main import app
from src.data.loader import data_loader

client = TestClient(app)

print("=== 1. CAPABILITY MATRIX (ALL 10 MINES) ===")
matrix_res = client.get("/api/real/capability-matrix").json()
print("Total mines:", matrix_res["total_mines"])
for item in matrix_res["matrix"]:
    print(f"\n{item['mine_id']} ({item['mine_name']}, {item['state']}): Tier={item['tier']}, Workflow={item['decision_workflow_status']}")
    for cap, val in item["capabilities"].items():
        print(f"    - {cap}: {val}")

print("\n=== 2. DECISION PAYLOAD ISOLATION CHECK ===")
for mid in ["MOIL_BALAGHAT", "MOIL_UKWA", "MOIL_SITAPATORE", "MOIL_KANDRI"]:
    res = client.get(f"/api/real/decision/{mid}").json()
    tier = res.get("tier")
    workflow = res.get("decision_workflow", {})
    stage4 = workflow.get("stage_4_analytical_signal", {})
    stage5 = workflow.get("stage_5_explanation", {})
    stage6 = workflow.get("stage_6_scenario", {})
    stage7 = workflow.get("stage_7_optimization", {})
    stage8 = workflow.get("stage_8_recommended_action", {})
    
    print(f"\n--- Mine: {mid} (Tier: {tier}) ---")
    print("  Stage 4 Exploration Signal:", stage4.get("exploration_analytical_signal", {}).get("signal_type") or stage4.get("exploration_analytical_signal", {}).get("status"))
    print("  Stage 4 Production Forecast:", stage4.get("production_forecast_signal", {}).get("forecast_model") or stage4.get("production_forecast_signal", {}).get("status"))
    print("  Stage 5 SHAP Explanation Status:", stage5.get("status") or ("AVAILABLE: " + str(stage5.get("method"))))
    print("  Stage 6 Scenario Status:", stage6.get("status") or ("AVAILABLE: " + str(stage6.get("scenario_name"))))
    print("  Stage 7 Optimization Status:", stage7.get("status") or ("AVAILABLE: " + str(stage7.get("solver_status"))))
    print("  Stage 8 Operational Status:", stage8.get("operational_status"))
    
    # Check if Block-A / Balaghat specific data leaked into other mines:
    raw_str = json.dumps(res).lower()
    if mid != "MOIL_BALAGHAT":
        has_block_a_leak = "block-a" in raw_str or "block a" in raw_str
        has_shap_values = "shap_values" in raw_str or "feature_attribution" in raw_str
        print(f"  [Isolation Audit] Has Block-A leak: {has_block_a_leak}, Has SHAP leak: {has_shap_values}")

print("\n=== 3. PRODUCTION REPORTED DATASET SCOPE & PERIODS ===")
prod_df = data_loader.load_real_production_df()
print("Production DataFrame columns:", prod_df.columns.tolist())
print("Unique scopes:", prod_df["scope"].unique().tolist() if "scope" in prod_df.columns else "N/A")
print("Unique period types:", prod_df["period_type"].unique().tolist() if "period_type" in prod_df.columns else "N/A")
print("Periods list:\n", prod_df[["period", "period_type", "production_tonnes", "scope"]].to_string())

print("\n=== 4. CANONICAL MOIL PRODUCTION CSV AUDIT ===")
prod_csv_path = data_loader.data_dir / "moil" / "production" / "production_reported.csv"
print(f"CSV Path: {prod_csv_path}")
print("Exists:", prod_csv_path.exists())
if prod_csv_path.exists():
    import pandas as pd
    raw_df = pd.read_csv(prod_csv_path)
    print("Rows:", len(raw_df))
    print("Periods in file:", raw_df["period"].unique().tolist())
