# SIH 2026 — PS 26009: API Contracts & System Specification

## AI/ML & Space Technology for Manganese Reserve Identification & Production-Shortfall Decision Support

### 1. Architectural Philosophy: The Closed Loop
Unlike conventional dashboards, the system executes a tightly integrated 5-stage closed loop:

$$\textbf{Predict} \longrightarrow \textbf{Explain} \longrightarrow \textbf{Simulate} \longrightarrow \textbf{Recommend} \longrightarrow \textbf{Visualize}$$

---

### 2. Endpoints Reference

#### `GET /`
- **Description**: Platform metadata and operational status.

#### `GET /api/health`
- **Description**: Verifies status of all models (LightGBM Quantile, XGBoost Spatial CV, SHAP TreeExplainer, PuLP MILP).

#### `GET /api/mine/overview?selected_block=BLOCK_A`
- **Description**: Consolidated KPI overview, active block statistics, fleet status, weather warnings, and aggregate shortfall risk.

#### `POST /api/forecast/production` & `GET /api/forecast/production`
- **Request**:
  ```json
  {
    "mine_block_id": "BLOCK_A",
    "horizon_days": 30,
    "target_tonnes": 10000.0
  }
  ```
- **Response**:
  ```json
  {
    "mine_block_id": "BLOCK_A",
    "forecast_tonnes": 8650.0,
    "interval_90": [7900.0, 9300.0],
    "target_tonnes": 10000.0,
    "expected_shortfall_tonnes": 1350.0,
    "shortfall_pct": 13.5,
    "shortfall_probability": 0.87,
    "risk_level": "HIGH",
    "horizon_days": 30,
    "daily_points": [...]
  }
  ```

#### `GET /api/explain/shortfall?mine_block_id=BLOCK_A&horizon_days=30`
- **Response**:
  ```json
  {
    "mine_block_id": "BLOCK_A",
    "target_tonnes": 10000.0,
    "forecast_tonnes": 8650.0,
    "expected_shortfall": 1350.0,
    "contributors": [
      {"factor": "equipment_downtime", "label": "Equipment Downtime & Repairs", "contribution_pct": 35, "raw_impact_tonnes": 472.5},
      {"factor": "blasting_delay", "label": "Blasting Operations Delay", "contribution_pct": 25, "raw_impact_tonnes": 337.5},
      {"factor": "rainfall_forecast", "label": "Rainfall & Wet Pit Logistics", "contribution_pct": 20, "raw_impact_tonnes": 270.0},
      {"factor": "equipment_availability", "label": "Fleet Mechanical Availability", "contribution_pct": 15, "raw_impact_tonnes": 202.5},
      {"factor": "historical_production_trend", "label": "Baseline Production Trend", "contribution_pct": 5, "raw_impact_tonnes": 67.5}
    ],
    "narrative": "The forecasted production of 8,650 t falls 1,350 t short of target (10,000 t)...",
    "note": "Model-attributed contributions (SHAP TreeExplainer), not verified physical causation."
  }
  ```

#### `GET /api/recommend/actions?mine_block_id=BLOCK_A&horizon_days=30`
- **Response**:
  ```json
  {
    "mine_block_id": "BLOCK_A",
    "target_tonnes": 10000.0,
    "baseline_forecast": 8650.0,
    "expected_shortfall": 1350.0,
    "top_2_projected_recovery": 1050.0,
    "residual_shortfall": 300.0,
    "options": [
      {
        "rank": 1,
        "action_id": "ACT_REDEPLOY_EXC",
        "action": "redeploy_excavator",
        "title": "Redeploy 120T Excavator: Block B -> Block A",
        "expected_recovery_tonnes": 600.0,
        "cost": "Low",
        "feasibility": "High",
        "net_utility_score": 530.5,
        "lp_recommended": true
      },
      {
        "rank": 2,
        "action_id": "ACT_RESCHEDULE_BLAST",
        "action": "reschedule_blasting",
        "title": "Reschedule Blasting Operation Window",
        "expected_recovery_tonnes": 450.0,
        "cost": "Medium",
        "feasibility": "High",
        "net_utility_score": 318.0,
        "lp_recommended": true
      },
      {
        "rank": 3,
        "action_id": "ACT_PREVENTIVE_MAINT",
        "action": "preventive_maintenance",
        "title": "Expedited Preventive Maintenance on Excavator-03",
        "expected_recovery_tonnes": 300.0,
        "cost": "Medium",
        "feasibility": "Medium",
        "net_utility_score": 138.0,
        "lp_recommended": false
      }
    ],
    "solver_status": "Optimal"
  }
  ```

#### `POST /api/simulate/scenario`
- **Description**: Real-time What-If sandbox re-scoring the trained LightGBM model with perturbed parameters.
- **Request**:
  ```json
  {
    "mine_block_id": "BLOCK_A",
    "horizon_days": 30,
    "equipment_availability_pct": 90.0,
    "blasting_delay_flag": 0,
    "rainfall_mm": 5.0
  }
  ```

#### `GET /api/prospectivity/map`
- **Description**: Returns GeoJSON FeatureCollection of 1,225 grid cells with prospectivity probability ($0.0 - 1.0$), uncertainty index, and Sentinel-2 proxy attributes.

#### `GET /api/prospectivity/drillholes`
- **Description**: Returns GeoJSON FeatureCollection of 240 drillhole assays with % Mn, % Fe, lithology, and depth intervals.

#### `GET /api/prospectivity/resource-estimate`
- **Description**: Returns illustrative geostatistical IDW/Ordinary Kriging resource summary (tonnes, average grade, volume) with explicit disclosure.
