# SIH 2026 — PS 26009
## AI/ML & Space Technology for Manganese Reserve Identification and Production-Shortfall Decision Support

An AI-assisted mining decision-support platform for Manganese Ore India Limited (MOIL) and open-cast/underground mining operations.

---

### Core Innovation: The 5-Stage Closed Loop
Rather than a disjointed dashboard or generic tabular model, this platform implements an end-to-end operational chain:

$$\textbf{Predict} \longrightarrow \textbf{Explain} \longrightarrow \textbf{Simulate} \longrightarrow \textbf{Recommend} \longrightarrow \textbf{Visualize}$$

1. **Predict (Module B & C)**: Probabilistic production forecasting via LightGBM Quantile Regression ($q=0.1, 0.5, 0.9$) on rolling-origin cross-validated time-series with exogenous weather, equipment, and blasting variables. Computes derived shortfall probability and expected deficit.
2. **Explain (Module D)**: SHAP TreeExplainer attributes model-predicted shortfalls into operational factors (equipment downtime, blasting delays, rainfall, reduced availability) with plain-language operational narratives and strict disclaimer distinguishing attribution from physical causation.
3. **Simulate (Module E)**: Interactive what-if sandbox re-scores the exact trained model under perturbed operational parameters in real time.
4. **Recommend (Module E)**: Constrained Mixed-Integer Linear Programming (PuLP MILP) ranks feasible, costed interventions (fleet redeployment, blast rescheduling, preventive maintenance) optimizing net utility.
5. **Visualize (Geospatial Digital Mine Map & UI)**: Interactive React + Leaflet + Recharts dashboard displaying active mine blocks, collar assays, prospectivity probability heatmap surfaces, production quantile confidence bands, and ranked action cards.

---

### Key Technical Safeguards
- **Spatial Block Cross-Validation**: Prospectivity model (XGBoost) is validated across disjoint spatial clusters (K-Means) to prevent spatial autocorrelation leakage.
- **Rolling-Origin Temporal Splits**: Production forecaster enforces forward-chaining historical splits to eliminate lookahead bias.
- **Physical Honesty**: Satellite indices (Sentinel-2 band ratios for iron oxide, clay, NDVI, NDWI, DEM slope/aspect, LST) are treated strictly as surface proxies, never claimed to "see" subsurface ore.
- **Toy Geostatistical Resource Estimation**: Grade interpolation (IDW/Kriging) and inferred tonnage are explicitly flagged as illustrative, non-JORC compliant toy models.
- **Synthetic Data Transparency**: Every synthetic dataset and dashboard view features a visible `[SYNTHETIC DEMO DATA]` badge.

---

### System Architecture
```
Data Sources (Drillhole Assays + Sentinel-2/DEM Grid + Daily Logs + Fleet Events)
        ↓
Feature Engineering (Lags, Rolling Windows, Spatial Joins, Spatial Block Clustering)
        ↓
ML Models (XGBoost Prospectivity + LightGBM Quantile Regression q=0.1, 0.5, 0.9)
        ↓
Shortfall Risk & SHAP Attribution (P(Shortfall < Target), Deficit %, TreeExplainer)
        ↓
Scenario Simulator & PuLP MILP Optimizer (Perturbed Re-scoring, Constrained Ranking)
        ↓
FastAPI Microservices (/api/forecast, /api/explain, /api/recommend, /api/prospectivity)
        ↓
Modern Interactive Digital Mine Dashboard (React, Leaflet, Recharts, Tailwind CSS)
```

---

### Quick Start Guide

#### 1. Backend Setup & Testing
```powershell
# Activate Python environment
.\.venv\Scripts\Activate.ps1

# Run synthetic data generator (if regenerating data)
python scripts/generate_synthetic_data.py

# Run training & cross-validation pipeline
python scripts/train_pipeline.py

# Run complete automated test suite
pytest tests/ -v

# Start FastAPI backend server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be available at: `http://localhost:8000/docs`.

#### 2. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```
Dashboard will be available at: `http://localhost:5173`.

#### 3. Docker Deployment
```bash
docker-compose -f docker/docker-compose.yml up --build
```

---

### End-to-End Live Demo Scenario (5-Minute Pitch Walkthrough)
1. **Target**: 10,000 tonnes (Block A monthly target).
2. **Forecast**: LightGBM quantile predicts ~8,650 tonnes (90% Interval: [7,900, 9,300]).
3. **Shortfall**: Risk Level **HIGH**, Shortfall Probability 87%, Expected Deficit 1,350 tonnes.
4. **SHAP Explainability**: Identifies Equipment Downtime (35%), Blasting Delay (25%), Rainfall (20%), and Reduced Availability (15%).
5. **Recommendations**:
   - **Rank 1**: Redeploy 120T Excavator (Block B $\rightarrow$ Block A) | +600 t recovery | Low Cost | High Feasibility
   - **Rank 2**: Reschedule Blasting Operation Window | +450 t recovery | Medium Cost | High Feasibility
   - **Rank 3**: Expedited Preventive Maintenance on EXC-03 | +300 t recovery | Medium Cost | Medium Feasibility
   - Combined Top-2 Projected Recovery: **+1,050 tonnes** (closing ~78% of the deficit).
6. **What-If Sandbox**: Adjust equipment availability slider from 72% to 90% to observe instant real-time recovery on the forecasting curve.
7. **Digital Mine Map**: Review drillhole assays with grade popups, toggle prospectivity heatmap cells (probability 0.0 to 1.0), and inspect fleet telemetry markers.
