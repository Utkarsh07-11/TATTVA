"""
Temporal Feature Engineering & Forward-Chaining Splitter
Prevents lookahead bias by strictly computing lag, rolling, and cyclical features
using past historical data only.
"""

from typing import List, Tuple, Generator
import numpy as np
import pandas as pd


class TemporalFeatureEngineer:
    """Computes lag and rolling window features for mining production time-series."""
    
    @staticmethod
    def create_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Expects a DataFrame with columns:
        ['date', 'mine_block_id', 'planned_tonnes', 'actual_tonnes',
         'equipment_availability_pct', 'rainfall_mm', 'blasting_delay_flag', 'maintenance_flag']
        Returns DataFrame with lag, rolling, and calendar features.
        """
        df = df.sort_values(["mine_block_id", "date"]).copy()
        
        # Calendar features
        df["day_of_week"] = df["date"].dt.dayofweek
        df["month"] = df["date"].dt.month
        df["is_monsoon"] = df["date"].dt.dayofyear.between(160, 270).astype(int)
        
        # Grouped lag features per block
        for block_id, block_group in df.groupby("mine_block_id"):
            # Target lags
            for lag in [1, 2, 7, 14, 30]:
                df.loc[block_group.index, f"tonnes_lag_{lag}"] = block_group["actual_tonnes"].shift(lag)
                
            # Availability lags
            for lag in [1, 2, 7]:
                df.loc[block_group.index, f"avail_lag_{lag}"] = block_group["equipment_availability_pct"].shift(lag)
                
            # Rolling window statistics (closed='left' to prevent current day leakage)
            for window in [7, 14]:
                # Actual production rolling stats
                roll_prod = block_group["actual_tonnes"].shift(1).rolling(window=window, min_periods=1)
                df.loc[block_group.index, f"prod_roll_mean_{window}d"] = roll_prod.mean()
                df.loc[block_group.index, f"prod_roll_std_{window}d"] = roll_prod.std().fillna(0.0)
                
                # Availability rolling stats
                roll_avail = block_group["equipment_availability_pct"].shift(1).rolling(window=window, min_periods=1)
                df.loc[block_group.index, f"avail_roll_mean_{window}d"] = roll_avail.mean()
                
                # Rainfall rolling sum
                roll_rain = block_group["rainfall_mm"].shift(1).rolling(window=window, min_periods=1)
                df.loc[block_group.index, f"rain_roll_sum_{window}d"] = roll_rain.sum()
                
                # Blasting delays count
                roll_blast = block_group["blasting_delay_flag"].shift(1).rolling(window=window, min_periods=1)
                df.loc[block_group.index, f"blast_delay_count_{window}d"] = roll_blast.sum()
                
        # Drop initial rows with unpopulated 30d lags
        df = df.dropna().reset_index(drop=True)
        return df

    @staticmethod
    def rolling_origin_splits(
        df: pd.DataFrame,
        n_splits: int = 5,
        test_window_days: int = 30
    ) -> Generator[Tuple[pd.DataFrame, pd.DataFrame], None, None]:
        """
        Implements forward-chaining / rolling-origin temporal cross-validation.
        Train on [t_start, t_k], validate on [t_k + 1, t_k + test_window_days].
        Guarantees zero future-information leakage.
        """
        unique_dates = df["date"].drop_duplicates().sort_values().reset_index(drop=True)
        total_dates = len(unique_dates)
        
        min_train_days = total_dates - (n_splits * test_window_days)
        if min_train_days < test_window_days * 2:
            raise ValueError("Not enough historical periods for specified splits and window size.")
            
        for i in range(n_splits):
            train_end_idx = min_train_days + (i * test_window_days)
            test_end_idx = train_end_idx + test_window_days
            
            train_dates = unique_dates.iloc[:train_end_idx]
            test_dates = unique_dates.iloc[train_end_idx:test_end_idx]
            
            train_df = df[df["date"].isin(train_dates)].copy()
            test_df = df[df["date"].isin(test_dates)].copy()
            
            yield train_df, test_df
