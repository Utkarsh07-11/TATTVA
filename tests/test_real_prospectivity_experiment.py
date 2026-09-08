"""
Test suite for Phase 9B Real-Data Prospectivity Experiment.
Verifies deterministic preprocessing, anomaly modeling, one-class anchor similarity,
spatial clustering, ranking monotonicity, no coordinate leakage, and metadata provenance.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.models.real_prospectivity_experiment import (
    RealProspectivityExperiment,
    PRIMARY_POSITIVE_ANCHOR_ID,
    PRIMARY_POSITIVE_EVIDENCE_ID,
    EXCLUDED_COORDINATE_COLS,
)

BASE_DIR = Path(__file__).resolve().parent.parent
REAL_GRID_PATH = BASE_DIR / "data" / "derived" / "geospatial" / "balaghat" / "real_feature_grid.csv"
MINERALIZATION_PATH = BASE_DIR / "data" / "real" / "geology" / "balaghat" / "mineralization_evidence.csv"
LABEL_CANDIDATES_PATH = BASE_DIR / "data" / "derived" / "geospatial" / "balaghat" / "mineralization_label_candidates.csv"

OUT_CSV_PATH = BASE_DIR / "data" / "derived" / "geospatial" / "balaghat" / "prospectivity_experiment.csv"
OUT_META_PATH = BASE_DIR / "data" / "derived" / "geospatial" / "balaghat" / "prospectivity_experiment_metadata.json"
OUT_SUM_PATH = BASE_DIR / "data" / "derived" / "geospatial" / "balaghat" / "prospectivity_experiment_summary.json"
OUT_REPORT_PATH = BASE_DIR / "data" / "derived" / "geospatial" / "balaghat" / "phase9b_report.md"


@pytest.fixture(scope="module")
def experiment_runner():
    return RealProspectivityExperiment(random_state=42, isolation_forest_trees=50)


@pytest.fixture(scope="module")
def experiment_results(experiment_runner):
    return experiment_runner.run_experiment(
        real_feature_grid_path=REAL_GRID_PATH,
        mineralization_evidence_path=MINERALIZATION_PATH,
        label_candidates_path=LABEL_CANDIDATES_PATH,
    )


def test_feature_preprocessing_and_aspect_transformation(experiment_runner):
    """Test deterministic aspect sin/cos transformation and trigonometric identity."""
    df_raw = pd.read_csv(REAL_GRID_PATH)
    X_scaled, df_work = experiment_runner.preprocess_features(df_raw)

    # Verify aspect_sin and aspect_cos columns created
    assert "aspect_sin" in df_work.columns
    assert "aspect_cos" in df_work.columns

    # Verify sin^2 + cos^2 == 1 for all valid rows
    trig_identity = (df_work["aspect_sin"] ** 2 + df_work["aspect_cos"] ** 2).values
    np.testing.assert_allclose(trig_identity, 1.0, atol=1e-5)

    # Verify no coordinates in feature names
    for excluded in EXCLUDED_COORDINATE_COLS:
        assert excluded not in experiment_runner.feature_names


def test_finite_model_inputs_and_scaling(experiment_runner):
    """Verify scaled matrix is finite and standardized (mean~0, std~1)."""
    df_raw = pd.read_csv(REAL_GRID_PATH)
    X_scaled, _ = experiment_runner.preprocess_features(df_raw)

    assert not np.isnan(X_scaled).any()
    assert not np.isinf(X_scaled).any()
    assert X_scaled.shape[0] == 27720
    assert X_scaled.shape[1] == len(experiment_runner.feature_names)

    # Check approximate zero-mean and unit variance
    means = np.mean(X_scaled, axis=0)
    stds = np.std(X_scaled, axis=0)
    np.testing.assert_allclose(means, 0.0, atol=1e-4)
    np.testing.assert_allclose(stds, 1.0, atol=1e-4)


def test_anomaly_score_generation_and_monotonicity(experiment_results):
    """Verify Isolation Forest and Robust Mahalanobis distance scores and ranks."""
    df_res = experiment_results["results_df"]

    # Scores within [0, 1]
    assert (df_res["anomaly_score"] >= 0.0).all() and (df_res["anomaly_score"] <= 1.0).all()
    assert (df_res["robust_distance_score"] >= 0.0).all() and (df_res["robust_distance_score"] <= 1.0).all()

    # Ranks between 1 and N
    n = len(df_res)
    assert df_res["anomaly_rank"].min() == 1
    assert df_res["anomaly_rank"].max() <= n
    assert df_res["robust_distance_rank"].min() == 1
    assert df_res["robust_distance_rank"].max() <= n

    # Monotonicity: higher anomaly score corresponds to lower rank number (closer to 1)
    # Check top 100 vs bottom 100
    top_anom = df_res.nsmallest(100, "anomaly_rank")
    bottom_anom = df_res.nlargest(100, "anomaly_rank")
    assert top_anom["anomaly_score"].min() > bottom_anom["anomaly_score"].max()

    top_rob = df_res.nsmallest(100, "robust_distance_rank")
    bottom_rob = df_res.nlargest(100, "robust_distance_rank")
    assert top_rob["robust_distance_score"].min() > bottom_rob["robust_distance_score"].max()


def test_positive_anchor_similarity_and_self_rank(experiment_results):
    """Verify single-anchor similarity gives highest rank to Bharweli portal anchor."""
    df_res = experiment_results["results_df"]
    summary = experiment_results["summary"]

    anchor_row = df_res[df_res["cell_id"] == PRIMARY_POSITIVE_ANCHOR_ID].iloc[0]

    # Anchor must be rank 1 in its own similarity metric
    assert int(anchor_row["positive_anchor_rank"]) == 1
    assert np.isclose(anchor_row["positive_anchor_similarity"], 1.0, atol=1e-4)
    assert summary["known_site_sanity_check"]["cell_id"] == PRIMARY_POSITIVE_ANCHOR_ID


def test_ensemble_formula_extremes():
    """Explicitly verify ensemble formula at theoretical extremes."""
    n_cells = 1000
    # Perfect rank 1 across all 3 models
    score_best = RealProspectivityExperiment.compute_ensemble_priority(
        np.array([1]), np.array([1]), np.array([1]), n_total_cells=n_cells
    )
    assert np.isclose(score_best[0], 1.0)

    # Worst rank N across all 3 models
    score_worst = RealProspectivityExperiment.compute_ensemble_priority(
        np.array([n_cells]), np.array([n_cells]), np.array([n_cells]), n_total_cells=n_cells
    )
    assert np.isclose(score_worst[0], 0.0)

    # Midpoint
    mid = (n_cells + 1) // 2
    score_mid = RealProspectivityExperiment.compute_ensemble_priority(
        np.array([mid]), np.array([mid]), np.array([mid]), n_total_cells=n_cells
    )
    assert 0.49 <= score_mid[0] <= 0.51


def test_dynamic_grid_geometry_derivation():
    """Verify grid geometry and 30m spacing derivation."""
    df_grid = pd.read_csv(REAL_GRID_PATH)
    n_rows, n_cols, res_m, xs, ys = RealProspectivityExperiment.derive_grid_geometry(df_grid)

    assert n_cols == 168
    assert n_rows == 165
    assert np.isclose(res_m, 30.0, atol=0.1)
    assert len(xs) == 168
    assert len(ys) == 165


def test_spatial_clustering_stability(experiment_results):
    """Verify connected-component cluster statistics for top percentiles."""
    summary = experiment_results["summary"]
    cl = summary["spatial_cluster_statistics"]

    assert "top_1_percent" in cl
    assert "top_5_percent" in cl
    assert "top_10_percent" in cl

    assert cl["top_1_percent"]["cell_count"] == 278
    assert cl["top_1_percent"]["num_clusters"] > 0
    assert cl["top_1_percent"]["largest_cluster_cells"] > 50  # Coherent ridge zone


def test_feature_quality_preservation(experiment_results):
    """Verify feature_quality is preserved and check quality in top priority cells."""
    df_res = experiment_results["results_df"]
    summary = experiment_results["summary"]

    assert set(df_res["feature_quality"].unique()) == {"valid", "partial"}
    assert (df_res["feature_quality"] == "valid").sum() == 27487
    assert (df_res["feature_quality"] == "partial").sum() == 233

    # Ensure partial cells do not dominate top 10%
    qual_top10 = summary["quality_in_top_priority"]
    assert qual_top10.get("valid", 0) > 2700


def test_zero_synthetic_dataset_dependency(experiment_results):
    """Verify metadata confirms real data sources and no synthetic dataset references."""
    meta = experiment_results["metadata"]
    assert "real_feature_grid.csv" in meta["source_datasets"]["feature_grid"]
    assert "mineralization_evidence.csv" in meta["source_datasets"]["mineralization_evidence"]
    assert "synthetic" not in meta["source_datasets"]["feature_grid"].lower()


def test_deterministic_random_seed():
    """Verify two independent runs with seed 42 produce identical ranks."""
    df_raw = pd.read_csv(REAL_GRID_PATH)
    exp1 = RealProspectivityExperiment(random_state=42, isolation_forest_trees=30)
    exp2 = RealProspectivityExperiment(random_state=42, isolation_forest_trees=30)

    X1, _ = exp1.preprocess_features(df_raw)
    X2, _ = exp2.preprocess_features(df_raw)

    _, ranks1 = exp1.compute_isolation_forest_anomaly(X1)
    _, ranks2 = exp2.compute_isolation_forest_anomaly(X2)

    np.testing.assert_array_equal(ranks1, ranks2)


def test_saved_artifacts_integrity():
    """Verify generated CSV, JSON, report, and diagnostic PNG maps exist and are valid."""
    assert OUT_CSV_PATH.exists()
    assert OUT_META_PATH.exists()
    assert OUT_SUM_PATH.exists()
    assert OUT_REPORT_PATH.exists()

    df = pd.read_csv(OUT_CSV_PATH)
    assert len(df) == 27720
    assert len(df["cell_id"].unique()) == 27720
    assert not df.isna().any().any()

    with open(OUT_META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert len(meta["critical_scientific_limitations"]) == 7

    with open(OUT_SUM_PATH, "r", encoding="utf-8") as f:
        summ = json.load(f)
    assert summ["known_site_sanity_check"]["cell_id"] == PRIMARY_POSITIVE_ANCHOR_ID

    diag_dir = BASE_DIR / "data" / "derived" / "geospatial" / "balaghat" / "diagnostics"
    assert (diag_dir / "anomaly_score_map.png").exists()
    assert (diag_dir / "robust_distance_map.png").exists()
    assert (diag_dir / "positive_anchor_similarity_map.png").exists()
    assert (diag_dir / "exploration_priority_map.png").exists()
    assert (diag_dir / "model_agreement_map.png").exists()
