"""
Unit and Integration Tests for Phase 12: Production Intelligence + Macro/Micro Reconciliation.
Validates:
1. Canonical reported production dataset preservation (11 observations, FY16 to FY26).
2. Strict separation of Macro (company aggregate historical) and Micro (operational simulation).
3. Absolute non-fabrication of mine-wise historical data from company totals.
4. Reconciliation arithmetic (variance = simulated - target, shortfall = max(0, target - simulated), excess = max(0, simulated - target)).
5. Scenario determinism and baseline vs scenario distinction.
6. Parameter validation and error handling.
7. Decision optimizer consistency.
"""

import pytest
import pandas as pd
from pathlib import Path
from fastapi.testclient import TestClient

from config.settings import settings
from src.api.main import app
from src.data.loader import data_loader

client = TestClient(app)


class TestCanonicalReportedProductionDataset:
    """Test 1 & 2: Ensure canonical reported production dataset remains intact and uncorrupted."""

    def test_canonical_csv_exists_and_unmodified(self):
        canonical_path = settings.REAL_DATA_DIR / "moil" / "production" / "production_reported.csv"
        assert canonical_path.exists(), "production_reported.csv must exist in data/real/moil/production/"

        df = pd.read_csv(canonical_path)
        annual_moil = df[(df["company"] == "MOIL Limited") & (df["period_type"] == "annual")]
        assert len(annual_moil) == 11, f"Expected 11 canonical annual observations for MOIL, got {len(annual_moil)}"

        # Verify exact FY series from FY2015-16 to FY2025-26
        expected_periods = [
            "FY2015-16",
            "FY2016-17",
            "FY2017-18",
            "FY2018-19",
            "FY2019-20",
            "FY2020-21",
            "FY2021-22",
            "FY2022-23",
            "FY2023-24",
            "FY2024-25",
            "FY2025-26",
        ]
        actual_periods = annual_moil["period"].tolist()
        assert actual_periods == expected_periods, f"Period series mismatch. Expected {expected_periods}, got {actual_periods}"

    def test_canonical_data_integrity_and_provenance(self):
        df = data_loader.load_real_production_df(period_type="annual", company="MOIL Limited")
        assert not df.empty
        assert len(df) == 11
        assert (df["company"] == "MOIL Limited").all()
        assert (df["mine"] == "ALL_MINES_AGGREGATE").all()
        assert (df["data_status"] == "reported").all()
        assert (df["period_type"] == "annual").all()

        # Check positive production numbers
        assert (df["production_tonnes"] > 0).all()
        # Verify FY2023-24 record
        fy24_row = df[df["period"] == "FY2023-24"].iloc[0]
        assert fy24_row["production_tonnes"] == 1756000.0


class TestNoHistoricalFabrication:
    """Test 3 & 4: Verify zero company-to-mine allocation or historical fabrication."""

    def test_no_mine_wise_allocation_in_loader(self):
        raw_df = data_loader.load_real_production_df()
        statutory_mines = [
            "MOIL_BALAGHAT",
            "MOIL_TIRODI",
            "MOIL_DONGRI_BUZURG",
            "MOIL_GUMGAON",
            "MOIL_KANDRI",
            "MOIL_MANSAR",
            "MOIL_CHIKLA",
            "MOIL_UKWA",
            "MOIL_BHARVELI",
            "MOIL_PARSODA",
        ]
        assert not any(m in raw_df["mine"].values for m in statutory_mines), (
            "Statutory mine IDs must NEVER be present as allocated historical production rows."
        )

    def test_reconciliation_endpoint_enforces_scope_separation(self):
        res = client.get("/api/real/production/reconciliation?mine_block_id=BLOCK_A&horizon_days=30")
        assert res.status_code == 200
        data = res.json()

        # Macro layer validation
        macro = data["macro_context"]
        assert macro["status"] == "REPORTED DATA"
        assert macro["scope"] == "COMPANY_LEVEL_AGGREGATE"
        assert macro["company"] == "MOIL Limited"
        assert macro["series_count"] == 11
        assert "not allocated to individual mines" in macro["scope_note"].lower()

        # Micro layer validation
        micro = data["micro_simulation"]
        assert micro["status"] == "SIMULATION"
        assert micro["scope"] == "BLOCK_OPERATIONAL"
        assert micro["mine_block_id"] == "BLOCK_A"
        assert micro["operational_target_tonnes"] == 10000.0

        # Governance validation
        gov = data["governance"]
        assert gov["macro_status"] == "REPORTED DATA"
        assert gov["micro_status"] == "TATTVA OPERATIONAL SIMULATION"
        assert "strict separation enforced" in gov["non_fabrication_policy"].lower()


class TestReconciliationArithmetic:
    """Test 5: Verify exact mathematical calculations for variance, shortfall, and excess."""

    def test_reconciliation_arithmetic_formulas(self):
        res = client.get("/api/real/production/reconciliation?mine_block_id=BLOCK_A&horizon_days=30")
        assert res.status_code == 200
        data = res.json()

        micro = data["micro_simulation"]
        rec = data["scenario_reconciliation"]

        target = rec["operational_target_tonnes"]
        output = rec["simulated_output_tonnes"]
        variance = rec["scenario_variance_tonnes"]
        shortfall = rec["scenario_shortfall_tonnes"]
        excess = rec["scenario_excess_tonnes"]

        # Exact formulas
        expected_variance = round(output - target, 1)
        expected_shortfall = max(0.0, round(target - output, 1))
        expected_excess = max(0.0, round(output - target, 1))

        assert variance == pytest.approx(expected_variance, rel=1e-3)
        assert shortfall == pytest.approx(expected_shortfall, rel=1e-3)
        assert excess == pytest.approx(expected_excess, rel=1e-3)

        if output >= target:
            assert shortfall == 0.0
            assert excess == pytest.approx(variance, rel=1e-3)
        else:
            assert excess == 0.0
            assert shortfall == pytest.approx(abs(variance), rel=1e-3)

    def test_custom_target_reconciliation(self):
        # Test with custom target lower than forecast (4928.4 MT) to force surplus
        res = client.get("/api/real/production/reconciliation?mine_block_id=BLOCK_A&horizon_days=30&target_tonnes=3000.0")
        assert res.status_code == 200
        data = res.json()
        rec = data["scenario_reconciliation"]

        assert rec["operational_target_tonnes"] == 3000.0
        assert rec["scenario_variance_tonnes"] > 0
        assert rec["scenario_shortfall_tonnes"] == 0.0
        assert rec["scenario_excess_tonnes"] == rec["scenario_variance_tonnes"]


class TestScenarioDeterminismAndOverrides:
    """Test 6 & 7: Verify scenario repeatability and separation from baseline."""

    def test_scenario_determinism(self):
        payload = {
            "mine_block_id": "BLOCK_A",
            "horizon_days": 30,
            "equipment_availability_pct": 70.0,
            "blasting_delay_flag": 1,
            "rainfall_mm": 50.0,
        }
        res1 = client.post("/api/real/production/reconciliation", json=payload)
        res2 = client.post("/api/real/production/reconciliation", json=payload)

        assert res1.status_code == 200
        assert res2.status_code == 200
        assert res1.json() == res2.json(), "Identical scenario parameters must yield strictly deterministic results"

    def test_baseline_vs_scenario_output_separation(self):
        base_res = client.get("/api/real/production/reconciliation?mine_block_id=BLOCK_A&horizon_days=30")
        assert base_res.status_code == 200
        base_data = base_res.json()
        base_output = base_data["scenario_reconciliation"]["simulated_output_tonnes"]

        # Degraded scenario: low equipment availability + blasting delay + heavy rain
        degraded_payload = {
            "mine_block_id": "BLOCK_A",
            "horizon_days": 30,
            "equipment_availability_pct": 50.0,
            "blasting_delay_flag": 1,
            "rainfall_mm": 120.0,
        }
        deg_res = client.post("/api/real/production/reconciliation", json=degraded_payload)
        assert deg_res.status_code == 200
        deg_data = deg_res.json()
        deg_output = deg_data["scenario_reconciliation"]["simulated_output_tonnes"]

        assert deg_data["scenario_reconciliation"]["has_scenario_overrides"] is True
        assert deg_output < base_output, "Degraded conditions must lower simulated operational production"


class TestErrorHandlingAndValidation:
    """Test 8: Verify robust handling of invalid parameters."""

    def test_invalid_mine_block_returns_404(self):
        res = client.get("/api/real/production/reconciliation?mine_block_id=NON_EXISTENT_BLOCK")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    def test_invalid_horizon_returns_422(self):
        res = client.get("/api/real/production/reconciliation?mine_block_id=BLOCK_A&horizon_days=999")
        assert res.status_code == 422


class TestOptimizerConsistency:
    """Test 9: Verify optimizer outputs actionable recommendations."""

    def test_optimizer_recommendations_structure(self):
        res = client.get("/api/real/production/reconciliation?mine_block_id=BLOCK_A&horizon_days=30")
        assert res.status_code == 200
        data = res.json()
        assert "optimizer_recommendations" in data
        recs = data["optimizer_recommendations"]
        assert isinstance(recs, list)
        if len(recs) > 0:
            rec = recs[0]
            assert "action_name" in rec or "action_id" in rec or "type" in rec
