# Derived Data Architecture Layer

## Purpose
The `data/derived/` directory is reserved for spatial aggregations, engineered geochemical/geophysical feature tables, and model-ready intermediate representations that are deterministically computed from verified `data/real/` inputs.

## Separation Rules
1. **Real Data (`data/real/`):** Immutable public facts, official disclosures, and verified cadastral lease records.
2. **Derived Data (`data/derived/`):** Computed representations, normalized grids, and spatial join results derived from real inputs.
3. **Synthetic Data (`data/synthetic/`):** Simulated test data and sandbox scenarios for offline development and testing.
