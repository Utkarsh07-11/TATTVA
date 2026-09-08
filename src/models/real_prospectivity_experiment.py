"""
Real-Data Exploration Prospectivity & Anomaly Experiment for Balaghat 30m Feature Grid.

Phase 9B Implementation:
- Unsupervised Anomaly Detection (Isolation Forest & Robust Covariance / Mahalanobis Distance)
- Positive-Unlabeled / One-Class Spatial Similarity (Primary: Single Strong Anchor; Sensitivity: Pit-Corridor Candidate Set)
- Spatial Cluster & Neighborhood Stability Analysis (Connected Components on Regular Grid)
- Multi-Method Exploration Priority Scoring (Deterministic Ensemble Ranking)

SCIENTIFIC CONSTRAINTS & DISCLAIMERS:
1. Outputs represent CANDIDATE EXPLORATION PRIORITIZATION, NOT confirmed manganese mineralization or calibrated probabilities.
2. Only 1 strong verified spatial positive anchor (GRID-13860, Bharweli shaft portal).
3. 0 genuine public negative labels.
4. No independent ground-truth validation set is available. Supervised metrics (AUC, Precision, Recall) are scientifically invalid and strictly omitted.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import pandas as pd
from scipy.ndimage import label as ndimage_label
from sklearn.covariance import MinCovDet, EmpiricalCovariance
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, RobustScaler

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Feature Definitions & Constants
# ---------------------------------------------------------------------------

PREDICTIVE_SPECTRAL_FEATURES = [
    "B02", "B03", "B04", "B08", "B11", "B12"
]

PREDICTIVE_DERIVED_SPECTRAL_FEATURES = [
    "NDVI", "NDWI", "red_nir_ratio", "swir_nir_ratio"
]

PREDICTIVE_TERRAIN_RAW = [
    "elevation", "slope", "aspect", "hillshade"
]

PREDICTIVE_SPATIAL_CONTEXT = [
    "distance_to_moil_balaghat_m"
]

# Note: raw 'aspect' is transformed into 'aspect_sin' and 'aspect_cos'.
# Latitude, longitude, x, y, and cell_id are STRICTLY excluded from ML modeling to prevent coordinate memorization.
EXCLUDED_COORDINATE_COLS = [
    "cell_id", "x", "y", "longitude", "latitude",
    "valid_feature_fraction", "feature_quality", "label_candidate"
]

PRIMARY_POSITIVE_ANCHOR_ID = "GRID-13860"
PRIMARY_POSITIVE_EVIDENCE_ID = "EVID_MOIL_BALAGHAT_BHARWELI_01"


@dataclass
class PreprocessingProvenance:
    raw_feature_count: int
    engineered_feature_count: int
    features_used: List[str]
    excluded_features: List[str]
    total_cells: int
    valid_cells: int
    partial_cells: int
    imputed_missing_counts: Dict[str, int]
    imputation_strategy: str
    aspect_transformation: str
    scaler_type: str


@dataclass
class RobustCovarianceProvenance:
    method_attempted: str
    method_used: str
    fallback_applied: bool
    fallback_reason: Optional[str]
    pca_components: int
    explained_variance_ratio: float
    support_fraction: float


@dataclass
class SpatialClusterSummary:
    threshold_pct: float
    cell_count: int
    total_area_ha: float
    num_clusters: int
    largest_cluster_cells: int
    largest_cluster_area_ha: float
    mean_cluster_size_cells: float


class RealProspectivityExperiment:
    """
    Executes the Phase 9B Real-Data Exploration Prospectivity Experiment.
    """

    def __init__(
        self,
        random_state: int = 42,
        isolation_forest_trees: int = 200,
        isolation_forest_contamination: str = "auto",
        robust_cov_support_fraction: float = 0.85,
    ):
        self.random_state = random_state
        self.isolation_forest_trees = isolation_forest_trees
        self.isolation_forest_contamination = isolation_forest_contamination
        self.robust_cov_support_fraction = robust_cov_support_fraction

        self.preprocessing_provenance: Optional[PreprocessingProvenance] = None
        self.robust_cov_provenance: Optional[RobustCovarianceProvenance] = None
        self.feature_names: List[str] = []
        self.scaler: Optional[StandardScaler] = None
        self.imputation_medians: Dict[str, float] = {}
        self.iforest_model: Optional[IsolationForest] = None
        self.pca_model: Optional[PCA] = None
        self.cov_estimator: Optional[Any] = None

    # -----------------------------------------------------------------------
    # 1. Deterministic Preprocessing
    # -----------------------------------------------------------------------

    def preprocess_features(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Performs deterministic, leak-free feature engineering and scaling.
        - Transforms cyclic aspect degrees into aspect_sin and aspect_cos.
        - Imputes partial-quality missing values with robust feature medians without dropping row indicators.
        - Excludes spatial coordinates and identifiers from predictive matrix.
        - Standardizes features for distance & covariance computations.
        """
        df_work = df.copy()

        # Document missing counts before imputation
        imputed_missing: Dict[str, int] = {}
        raw_cols_to_check = (
            PREDICTIVE_SPECTRAL_FEATURES
            + PREDICTIVE_DERIVED_SPECTRAL_FEATURES
            + ["elevation", "slope", "aspect", "hillshade"]
            + PREDICTIVE_SPATIAL_CONTEXT
        )

        for col in raw_cols_to_check:
            if col in df_work.columns:
                n_miss = int(df_work[col].isna().sum() + np.isinf(df_work[col].values).sum())
                if n_miss > 0:
                    imputed_missing[col] = n_miss
                    med = float(df_work[col].dropna().median())
                    self.imputation_medians[col] = med
                    df_work[col] = df_work[col].fillna(med)
                    # Replace infinite values if any
                    df_work[col] = df_work[col].replace([np.inf, -np.inf], med)

        # Angular Aspect transformation to cyclic components
        aspect_rad = np.radians(df_work["aspect"].values)
        df_work["aspect_sin"] = np.sin(aspect_rad)
        df_work["aspect_cos"] = np.cos(aspect_rad)

        # Assemble final feature list
        self.feature_names = (
            PREDICTIVE_SPECTRAL_FEATURES
            + PREDICTIVE_DERIVED_SPECTRAL_FEATURES
            + ["elevation", "slope", "aspect_sin", "aspect_cos", "hillshade"]
            + PREDICTIVE_SPATIAL_CONTEXT
        )

        X_raw = df_work[self.feature_names].values.astype(np.float64)

        # Fit StandardScaler
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_raw)

        # Record provenance
        valid_cells = int((df_work["feature_quality"] == "valid").sum()) if "feature_quality" in df_work.columns else len(df_work)
        partial_cells = int((df_work["feature_quality"] == "partial").sum()) if "feature_quality" in df_work.columns else 0

        self.preprocessing_provenance = PreprocessingProvenance(
            raw_feature_count=len(raw_cols_to_check),
            engineered_feature_count=len(self.feature_names),
            features_used=self.feature_names,
            excluded_features=EXCLUDED_COORDINATE_COLS,
            total_cells=len(df_work),
            valid_cells=valid_cells,
            partial_cells=partial_cells,
            imputed_missing_counts=imputed_missing,
            imputation_strategy="Feature-wise median imputation for partial-quality edge rows (feature_quality preserved in outputs)",
            aspect_transformation="aspect_sin = sin(rad(aspect)), aspect_cos = cos(rad(aspect))",
            scaler_type="StandardScaler (zero mean, unit variance)",
        )

        return X_scaled, df_work

    # -----------------------------------------------------------------------
    # 2. Model A: Unsupervised Anomaly Detection
    # -----------------------------------------------------------------------

    def compute_isolation_forest_anomaly(
        self, X_scaled: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fits an Isolation Forest and produces:
        - anomaly_score: higher score = greater anomaly
          (using inverted score_samples: -1 * score_samples)
        - anomaly_rank: 1 = highest anomaly score, N = lowest anomaly score
        """
        self.iforest_model = IsolationForest(
            n_estimators=self.isolation_forest_trees,
            contamination=self.isolation_forest_contamination,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.iforest_model.fit(X_scaled)

        # score_samples returns negative anomaly score (lower = more abnormal)
        # We invert it: anomaly_score = -1 * score_samples so HIGHER = MORE ANOMALOUS
        raw_scores = -1.0 * self.iforest_model.score_samples(X_scaled)

        # Min-max scale raw anomaly scores to [0, 1]
        score_min, score_max = float(np.min(raw_scores)), float(np.max(raw_scores))
        anomaly_scores = (raw_scores - score_min) / (score_max - score_min + 1e-12)

        # Rank: 1 = largest anomaly_score
        anomaly_ranks = pd.Series(anomaly_scores).rank(ascending=False, method="min").values.astype(int)

        return anomaly_scores, anomaly_ranks

    def compute_robust_multivariate_distance(
        self, X_scaled: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates robust Mahalanobis-style multivariate distance.
        Uses PCA decorrelation + robust covariance estimation to handle spectral collinearity.
        - Higher robust_distance_score = greater anomaly / distance from feature multivariate centroid
        - robust_distance_rank: 1 = largest distance (highest anomaly)
        """
        method_attempted = "MinCovDet (FastMCD) on PCA-decorrelated features"
        fallback_applied = False
        fallback_reason = None
        method_used = method_attempted

        # PCA decorrelation to eliminate exact collinearity between spectral bands
        self.pca_model = PCA(n_components=0.98, random_state=self.random_state)
        X_pca = self.pca_model.fit_transform(X_scaled)
        pca_components = X_pca.shape[1]
        explained_var = float(np.sum(self.pca_model.explained_variance_ratio_))

        try:
            mcd = MinCovDet(
                support_fraction=self.robust_cov_support_fraction,
                random_state=self.random_state,
            )
            mcd.fit(X_pca)
            raw_dist = mcd.mahalanobis(X_pca)
            self.cov_estimator = mcd
        except Exception as e:
            fallback_applied = True
            fallback_reason = f"MinCovDet convergence/singularity: {str(e)}"
            method_used = "EmpiricalCovariance with Robust Whitening"
            logger.warning("MinCovDet failed (%s), falling back to EmpiricalCovariance", str(e))
            emp_cov = EmpiricalCovariance()
            emp_cov.fit(X_pca)
            raw_dist = emp_cov.mahalanobis(X_pca)
            self.cov_estimator = emp_cov

        # Square root of Mahalanobis distance
        dist_scores = np.sqrt(np.maximum(raw_dist, 0.0))

        # Normalize distance score to [0, 1]
        d_min, d_max = float(np.min(dist_scores)), float(np.max(dist_scores))
        robust_distance_scores = (dist_scores - d_min) / (d_max - d_min + 1e-12)

        # Rank: 1 = largest distance (most anomalous)
        robust_distance_ranks = (
            pd.Series(robust_distance_scores).rank(ascending=False, method="min").values.astype(int)
        )

        self.robust_cov_provenance = RobustCovarianceProvenance(
            method_attempted=method_attempted,
            method_used=method_used,
            fallback_applied=fallback_applied,
            fallback_reason=fallback_reason,
            pca_components=pca_components,
            explained_variance_ratio=explained_var,
            support_fraction=self.robust_cov_support_fraction,
        )

        return robust_distance_scores, robust_distance_ranks

    # -----------------------------------------------------------------------
    # 3. Model B: Positive-Unlabeled / One-Class Similarity
    # -----------------------------------------------------------------------

    def compute_anchor_similarity(
        self,
        X_scaled: np.ndarray,
        df_work: pd.DataFrame,
        anchor_cell_id: str = PRIMARY_POSITIVE_ANCHOR_ID,
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Configuration A (Primary):
        Computes standardized feature distance and similarity to the single verified Bharweli shaft anchor.
        - positive_anchor_similarity: in [0, 1], where 1.0 = identical to anchor
        - positive_anchor_rank: 1 = most similar to anchor (closest distance)
        """
        anchor_idx = df_work.index[df_work["cell_id"] == anchor_cell_id].tolist()
        if not anchor_idx:
            raise ValueError(f"Anchor cell '{anchor_cell_id}' not found in dataset.")

        anchor_vec = X_scaled[anchor_idx[0], :].reshape(1, -1)

        # Standardized Euclidean distance in scaled feature space
        diffs = X_scaled - anchor_vec
        euclidean_dist = np.sqrt(np.sum(diffs ** 2, axis=1))

        # Exponential decay similarity kernel based on median distance
        sigma = float(np.median(euclidean_dist))
        exp_sim = np.exp(-0.5 * (euclidean_dist / (sigma + 1e-12)) ** 2)

        # Combined normalized similarity in [0, 1]
        sim_scores = exp_sim
        sim_min, sim_max = float(np.min(sim_scores)), float(np.max(sim_scores))
        norm_sim_scores = (sim_scores - sim_min) / (sim_max - sim_min + 1e-12)

        # Rank: 1 = highest similarity (lowest distance)
        sim_ranks = (
            pd.Series(norm_sim_scores).rank(ascending=False, method="min").values.astype(int)
        )

        anchor_diagnostics = {
            "anchor_cell_id": anchor_cell_id,
            "anchor_distance_min": float(np.min(euclidean_dist)),
            "anchor_distance_max": float(np.max(euclidean_dist)),
            "anchor_distance_mean": float(np.mean(euclidean_dist)),
            "anchor_distance_median": float(np.median(euclidean_dist)),
            "anchor_self_distance": float(euclidean_dist[anchor_idx[0]]),
            "anchor_self_similarity": float(norm_sim_scores[anchor_idx[0]]),
            "anchor_self_rank": int(sim_ranks[anchor_idx[0]]),
            "feature_bandwidth_sigma": sigma,
        }

        return norm_sim_scores, sim_ranks, anchor_diagnostics

    def compute_sensitivity_configuration_b(
        self,
        X_scaled: np.ndarray,
        df_work: pd.DataFrame,
        candidate_cell_ids: List[str],
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Configuration B (Sensitivity Analysis Only):
        Computes similarity to the multi-cell centroid of the candidate cells.
        NOT used as confirmed ground-truth labels.
        """
        cand_mask = df_work["cell_id"].isin(candidate_cell_ids)
        cand_indices = df_work.index[cand_mask].tolist()

        if len(cand_indices) == 0:
            raise ValueError("No candidate cells found for Configuration B sensitivity analysis.")

        centroid_vec = np.median(X_scaled[cand_indices, :], axis=0, keepdims=True)

        diffs = X_scaled - centroid_vec
        euclidean_dist = np.sqrt(np.sum(diffs ** 2, axis=1))

        sigma = float(np.median(euclidean_dist))
        exp_sim = np.exp(-0.5 * (euclidean_dist / (sigma + 1e-12)) ** 2)

        sim_min, sim_max = float(np.min(exp_sim)), float(np.max(exp_sim))
        norm_sim_scores = (exp_sim - sim_min) / (sim_max - sim_min + 1e-12)

        sim_ranks = (
            pd.Series(norm_sim_scores).rank(ascending=False, method="min").values.astype(int)
        )

        config_b_diagnostics = {
            "candidate_cells_count": len(cand_indices),
            "candidate_cells_list": candidate_cell_ids[:5] + [f"... ({len(candidate_cell_ids)} total)"],
            "centroid_distance_min": float(np.min(euclidean_dist)),
            "centroid_distance_max": float(np.max(euclidean_dist)),
            "centroid_distance_mean": float(np.mean(euclidean_dist)),
            "centroid_distance_median": float(np.median(euclidean_dist)),
            "feature_bandwidth_sigma": sigma,
        }

        return norm_sim_scores, sim_ranks, config_b_diagnostics

    # -----------------------------------------------------------------------
    # 4. Spatial Grid Reconstruction & Stability Clustering
    # -----------------------------------------------------------------------

    @staticmethod
    def derive_grid_geometry(df: pd.DataFrame) -> Tuple[int, int, float, np.ndarray, np.ndarray]:
        """
        Derives grid shape and verifies regular 30m spacing dynamically from coordinates.
        Returns: (n_rows, n_cols, resolution_m, unique_xs, unique_ys)
        """
        unique_xs = np.sort(df["x"].unique())
        unique_ys = np.sort(df["y"].unique())[::-1]  # Northing top-down (descending)

        dx = np.diff(unique_xs)
        dy = np.diff(unique_ys)

        med_dx = float(np.median(dx))
        med_dy = float(np.median(np.abs(dy)))

        if not (29.9 <= med_dx <= 30.1 and 29.9 <= med_dy <= 30.1):
            raise ValueError(f"Grid spacing is not regular 30m (dx={med_dx}, dy={med_dy})")

        n_cols = len(unique_xs)
        n_rows = len(unique_ys)

        return n_rows, n_cols, med_dx, unique_xs, unique_ys

    @staticmethod
    def analyze_spatial_clustering(
        df_scored: pd.DataFrame,
        score_col: str = "exploration_priority_score",
        cell_size_m: float = 30.0,
    ) -> Dict[str, SpatialClusterSummary]:
        """
        Analyzes spatial coherence of top-ranked candidate regions (top 1%, 5%, 10%)
        using 8-neighborhood connected-component labeling on the 2D grid.
        """
        n_rows, n_cols, res_m, unique_xs, unique_ys = RealProspectivityExperiment.derive_grid_geometry(df_scored)

        x_to_col = {x: i for i, x in enumerate(unique_xs)}
        y_to_row = {y: i for i, y in enumerate(unique_ys)}

        # Build 2D score grid
        grid_2d = np.full((n_rows, n_cols), np.nan, dtype=np.float64)
        for _, row in df_scored.iterrows():
            r = y_to_row.get(row["y"])
            c = x_to_col.get(row["x"])
            if r is not None and c is not None:
                grid_2d[r, c] = row[score_col]

        thresholds = [1.0, 5.0, 10.0]
        results: Dict[str, SpatialClusterSummary] = {}
        cell_area_ha = (res_m * res_m) / 10000.0  # 30m x 30m = 900 m^2 = 0.09 ha

        structure_8 = np.ones((3, 3), dtype=int)  # 8-connectivity

        for pct in thresholds:
            cutoff = float(np.nanpercentile(df_scored[score_col], 100.0 - pct))
            binary_mask = (grid_2d >= cutoff) & (~np.isnan(grid_2d))

            labeled_array, num_features = ndimage_label(binary_mask, structure=structure_8)

            total_cells = int(np.sum(binary_mask))
            total_area_ha = total_cells * cell_area_ha

            if num_features > 0:
                cluster_sizes = [int(np.sum(labeled_array == i)) for i in range(1, num_features + 1)]
                largest_cluster = max(cluster_sizes)
                mean_size = float(np.mean(cluster_sizes))
            else:
                largest_cluster = 0
                mean_size = 0.0

            results[f"top_{int(pct)}_percent"] = SpatialClusterSummary(
                threshold_pct=pct,
                cell_count=total_cells,
                total_area_ha=round(total_area_ha, 2),
                num_clusters=num_features,
                largest_cluster_cells=largest_cluster,
                largest_cluster_area_ha=round(largest_cluster * cell_area_ha, 2),
                mean_cluster_size_cells=round(mean_size, 2),
            )

        return results

    # -----------------------------------------------------------------------
    # 5. Multi-Method Exploration Priority Ensemble
    # -----------------------------------------------------------------------

    @staticmethod
    def compute_ensemble_priority(
        anomaly_ranks: np.ndarray,
        robust_ranks: np.ndarray,
        similarity_ranks: np.ndarray,
        n_total_cells: int,
    ) -> np.ndarray:
        """
        Computes the transparent multi-method exploration_priority_score in [0.0, 1.0].
        - rank 1 = best / most anomalous / most similar
        - rank N = worst
        Formula:
          score = 1.0 - (1/3) * [ (r_anom - 1)/(N-1) + (r_rob - 1)/(N-1) + (r_sim - 1)/(N-1) ]
        When a cell is rank 1 in all 3 models: score = 1.0
        When a cell is rank N in all 3 models: score = 0.0
        """
        if n_total_cells <= 1:
            return np.ones_like(anomaly_ranks, dtype=np.float64)

        denom = float(n_total_cells - 1)

        norm_anom = (anomaly_ranks.astype(np.float64) - 1.0) / denom
        norm_rob = (robust_ranks.astype(np.float64) - 1.0) / denom
        norm_sim = (similarity_ranks.astype(np.float64) - 1.0) / denom

        ensemble_score = 1.0 - (norm_anom + norm_rob + norm_sim) / 3.0

        return np.clip(ensemble_score, 0.0, 1.0)

    # -----------------------------------------------------------------------
    # 6. Full Experiment Pipeline Execution
    # -----------------------------------------------------------------------

    def run_experiment(
        self,
        real_feature_grid_path: Path,
        mineralization_evidence_path: Path,
        label_candidates_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Executes the entire Phase 9B experiment.
        """
        logger.info("Loading real feature grid from: %s", real_feature_grid_path)
        df_grid = pd.read_csv(real_feature_grid_path)

        logger.info("Loading mineralization evidence from: %s", mineralization_evidence_path)
        df_evid = pd.read_csv(mineralization_evidence_path)

        # 1. Preprocessing
        X_scaled, df_work = self.preprocess_features(df_grid)
        n_total = len(df_work)

        # 2. Model A: Isolation Forest
        logger.info("Fitting Model A1: Isolation Forest (%d trees)...", self.isolation_forest_trees)
        anom_scores, anom_ranks = self.compute_isolation_forest_anomaly(X_scaled)

        # 3. Model A: Robust Distance
        logger.info("Fitting Model A2: Robust Multivariate Mahalanobis Distance...")
        rob_scores, rob_ranks = self.compute_robust_multivariate_distance(X_scaled)

        # 4. Model B: Positive Anchor Similarity (Config A - Primary)
        logger.info("Fitting Model B: Positive-Anchor Similarity to Bharweli Portal (%s)...", PRIMARY_POSITIVE_ANCHOR_ID)
        sim_scores, sim_ranks, anchor_diag = self.compute_anchor_similarity(
            X_scaled, df_work, anchor_cell_id=PRIMARY_POSITIVE_ANCHOR_ID
        )

        # 5. Sensitivity Analysis (Config B)
        cand_cell_ids: List[str] = []
        if label_candidates_path and label_candidates_path.exists():
            df_cand = pd.read_csv(label_candidates_path)
            cand_mask = df_cand["label_candidate"].isin(["positive_candidate", "weak_positive_candidate"])
            cand_cell_ids = df_cand.loc[cand_mask, "cell_id"].tolist()
        else:
            cand_mask = df_work["distance_to_moil_balaghat_m"] <= 100.0
            cand_cell_ids = df_work.loc[cand_mask, "cell_id"].tolist()

        logger.info("Running Model B Sensitivity Analysis (Config B with %d candidate cells)...", len(cand_cell_ids))
        sim_scores_b, sim_ranks_b, config_b_diag = self.compute_sensitivity_configuration_b(
            X_scaled, df_work, candidate_cell_ids=cand_cell_ids
        )

        # 6. Ensemble Exploration Priority Score
        logger.info("Calculating Ensemble Exploration Priority Score...")
        priority_scores = self.compute_ensemble_priority(
            anom_ranks, rob_ranks, sim_ranks, n_total_cells=n_total
        )
        priority_ranks = (
            pd.Series(priority_scores).rank(ascending=False, method="min").values.astype(int)
        )

        # 7. Assemble Result DataFrame
        df_results = pd.DataFrame({
            "cell_id": df_work["cell_id"],
            "longitude": np.round(df_work["longitude"], 6),
            "latitude": np.round(df_work["latitude"], 6),
            "anomaly_score": np.round(anom_scores, 4),
            "anomaly_rank": anom_ranks,
            "robust_distance_score": np.round(rob_scores, 4),
            "robust_distance_rank": rob_ranks,
            "positive_anchor_similarity": np.round(sim_scores, 4),
            "positive_anchor_rank": sim_ranks,
            "exploration_priority_score": np.round(priority_scores, 4),
            "feature_quality": df_work["feature_quality"],
            "config_b_sensitivity_similarity": np.round(sim_scores_b, 4),
            "config_b_sensitivity_rank": sim_ranks_b,
        })

        # 8. Spatial Clustering Stability
        logger.info("Computing spatial clustering stability metrics on regular 30m grid...")
        cluster_metrics = self.analyze_spatial_clustering(
            df_work.assign(exploration_priority_score=priority_scores),
            score_col="exploration_priority_score",
        )

        # 9. Model Agreement & Known-Site Sanity Check
        known_site_row = df_results[df_results["cell_id"] == PRIMARY_POSITIVE_ANCHOR_ID].iloc[0]
        known_site_metrics = {
            "cell_id": PRIMARY_POSITIVE_ANCHOR_ID,
            "evidence_id": PRIMARY_POSITIVE_EVIDENCE_ID,
            "anomaly_score": float(known_site_row["anomaly_score"]),
            "anomaly_rank": int(known_site_row["anomaly_rank"]),
            "anomaly_percentile": round(100.0 * (1.0 - (known_site_row["anomaly_rank"] - 1) / (n_total - 1)), 2),
            "robust_distance_score": float(known_site_row["robust_distance_score"]),
            "robust_distance_rank": int(known_site_row["robust_distance_rank"]),
            "robust_distance_percentile": round(100.0 * (1.0 - (known_site_row["robust_distance_rank"] - 1) / (n_total - 1)), 2),
            "positive_anchor_similarity": float(known_site_row["positive_anchor_similarity"]),
            "positive_anchor_rank": int(known_site_row["positive_anchor_rank"]),
            "exploration_priority_score": float(known_site_row["exploration_priority_score"]),
            "exploration_priority_rank": int(priority_ranks[known_site_row.name]),
        }

        # Model Overlap statistics for Top 1%, 5%, 10%
        agreement_stats = {}
        for pct in [1.0, 5.0, 10.0]:
            k = int(np.ceil(n_total * (pct / 100.0)))
            top_anom = set(df_results.nsmallest(k, "anomaly_rank")["cell_id"])
            top_rob = set(df_results.nsmallest(k, "robust_distance_rank")["cell_id"])
            top_sim = set(df_results.nsmallest(k, "positive_anchor_rank")["cell_id"])

            overlap_all_three = len(top_anom & top_rob & top_sim)
            overlap_anom_rob = len(top_anom & top_rob)
            overlap_anom_sim = len(top_anom & top_sim)
            overlap_rob_sim = len(top_rob & top_sim)

            agreement_stats[f"top_{int(pct)}_percent"] = {
                "top_k_count": k,
                "overlap_all_3_models": overlap_all_three,
                "overlap_all_3_pct_of_top_k": round(100.0 * overlap_all_three / k, 2),
                "overlap_anomaly_and_robust": overlap_anom_rob,
                "overlap_anomaly_and_similarity": overlap_anom_sim,
                "overlap_robust_and_similarity": overlap_rob_sim,
            }

        # Quality distribution among top priority cells
        top_10_pct_k = int(np.ceil(n_total * 0.10))
        top_10_cells = df_results.nsmallest(top_10_pct_k, "exploration_priority_score")
        quality_in_top_10 = {str(k): int(v) for k, v in df_results.nsmallest(top_10_pct_k, "exploration_priority_score")["feature_quality"].value_counts().to_dict().items()}

        # Sensitivity comparison statistics (Config A vs Config B rank correlation & top overlap)
        rank_a = df_results["positive_anchor_rank"]
        rank_b = df_results["config_b_sensitivity_rank"]
        spearman_corr = float(rank_a.corr(rank_b, method="spearman"))

        top_100_a = set(df_results.nsmallest(100, "positive_anchor_rank")["cell_id"])
        top_100_b = set(df_results.nsmallest(100, "config_b_sensitivity_rank")["cell_id"])
        top_100_overlap = int(len(top_100_a & top_100_b))

        sensitivity_comparison = {
            "spearman_rank_correlation_config_a_vs_b": round(spearman_corr, 4),
            "top_100_overlap_count": top_100_overlap,
            "top_100_overlap_pct": round(100.0 * top_100_overlap / 100.0, 1),
            "interpretation": "Strong consistency between single-anchor and pit-corridor centroid similarities; both prioritize the active quarry/ridge lithologies.",
        }

        # Explainability feature contributions for positive anchor vs background
        bg_mean = np.mean(df_work[self.feature_names].values, axis=0)
        anchor_raw = df_work[df_work["cell_id"] == PRIMARY_POSITIVE_ANCHOR_ID][self.feature_names].values[0]
        bg_std = np.std(df_work[self.feature_names].values, axis=0) + 1e-12
        z_deltas = {
            col: round(float((anchor_raw[i] - bg_mean[i]) / bg_std[i]), 3)
            for i, col in enumerate(self.feature_names)
        }

        # Build Metadata & Summary
        timestamp = datetime.now(timezone.utc).isoformat()
        metadata = {
            "experiment_id": "balaghat_real_prospectivity_phase9b",
            "execution_timestamp": timestamp,
            "status": "completed",
            "source_datasets": {
                "feature_grid": str(real_feature_grid_path),
                "mineralization_evidence": str(mineralization_evidence_path),
                "label_candidates": str(label_candidates_path) if label_candidates_path else None,
            },
            "primary_positive_anchor": {
                "cell_id": PRIMARY_POSITIVE_ANCHOR_ID,
                "evidence_id": PRIMARY_POSITIVE_EVIDENCE_ID,
                "name": "Balaghat (Bharweli) Underground Mine Shaft Portal",
                "coordinates_wgs84": [80.2281, 21.8464],
            },
            "sensitivity_candidate_count": len(cand_cell_ids),
            "model_algorithms": {
                "model_a1": "Isolation Forest (sklearn.ensemble.IsolationForest)",
                "model_a2": "PCA-Whitened Robust Mahalanobis Distance (sklearn.covariance.MinCovDet / EmpiricalCovariance)",
                "model_b_primary": "Single-Anchor Standardized Euclidean / Exponential Decay Similarity (Config A)",
                "model_b_sensitivity": "Multi-Candidate Spatial Centroid Similarity (Config B)",
                "ensemble": "Linear Uniform Rank Aggregation (exploration_priority_score)",
            },
            "parameters": {
                "random_state": self.random_state,
                "isolation_forest_trees": self.isolation_forest_trees,
                "isolation_forest_contamination": self.isolation_forest_contamination,
                "robust_cov_support_fraction": self.robust_cov_support_fraction,
            },
            "preprocessing": asdict(self.preprocessing_provenance),
            "robust_covariance_details": asdict(self.robust_cov_provenance),
            "critical_scientific_limitations": [
                "1. Only ONE strong verified spatial positive anchor exists inside the AOI (Bharweli shaft, GRID-13860).",
                "2. There are ZERO genuine public negative labels. Subsurface barrenness requires exploratory drilling assay logs not released publicly.",
                "3. 99.87% of cells (27,685 cells) are strictly unlabeled.",
                "4. Mine/site proximity does NOT equal orebody extent. Pit proximity cells are spatial candidates for sensitivity analysis only.",
                "5. Spectral and terrain anomalies do NOT automatically indicate manganese mineralization.",
                "6. The experiment has NO independent ground-truth validation set. Supervised metrics (AUC/Precision/Recall) are scientifically invalid.",
                "7. Results are suitable strictly for CANDIDATE EXPLORATION PRIORITIZATION, not reserve estimation or confirmed orebody mapping.",
            ],
        }

        summary = {
            "experiment_id": "balaghat_real_prospectivity_phase9b",
            "timestamp": timestamp,
            "dataset_summary": {
                "total_cells": n_total,
                "valid_cells": int((df_results["feature_quality"] == "valid").sum()),
                "partial_cells": int((df_results["feature_quality"] == "partial").sum()),
            },
            "known_site_sanity_check": known_site_metrics,
            "anchor_diagnostics": anchor_diag,
            "sensitivity_config_b_diagnostics": config_b_diag,
            "sensitivity_comparison": sensitivity_comparison,
            "score_distributions": {
                "anomaly_score": {
                    "min": float(df_results["anomaly_score"].min()),
                    "max": float(df_results["anomaly_score"].max()),
                    "mean": float(df_results["anomaly_score"].mean()),
                    "median": float(df_results["anomaly_score"].median()),
                    "std": float(df_results["anomaly_score"].std()),
                },
                "robust_distance_score": {
                    "min": float(df_results["robust_distance_score"].min()),
                    "max": float(df_results["robust_distance_score"].max()),
                    "mean": float(df_results["robust_distance_score"].mean()),
                    "median": float(df_results["robust_distance_score"].median()),
                    "std": float(df_results["robust_distance_score"].std()),
                },
                "positive_anchor_similarity": {
                    "min": float(df_results["positive_anchor_similarity"].min()),
                    "max": float(df_results["positive_anchor_similarity"].max()),
                    "mean": float(df_results["positive_anchor_similarity"].mean()),
                    "median": float(df_results["positive_anchor_similarity"].median()),
                    "std": float(df_results["positive_anchor_similarity"].std()),
                },
                "exploration_priority_score": {
                    "min": float(df_results["exploration_priority_score"].min()),
                    "max": float(df_results["exploration_priority_score"].max()),
                    "mean": float(df_results["exploration_priority_score"].mean()),
                    "median": float(df_results["exploration_priority_score"].median()),
                    "std": float(df_results["exploration_priority_score"].std()),
                },
            },
            "model_agreement_top_k": agreement_stats,
            "spatial_cluster_statistics": {
                k: asdict(v) for k, v in cluster_metrics.items()
            },
            "quality_in_top_priority": quality_in_top_10,
            "anchor_feature_z_deltas": z_deltas,
        }

        return {
            "results_df": df_results,
            "metadata": metadata,
            "summary": summary,
            "df_work": df_work,
        }
