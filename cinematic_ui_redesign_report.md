# TATTVA UI Redesign: Cinematic Industrial Mining Intelligence Report

## Executive Summary
The TATTVA frontend has been completely redesigned from a generic SaaS/AI dashboard into a **Cinematic Industrial Mining Intelligence Command Platform**. Inspired by heavy-engineering workstations, modern mining technology interfaces, and cinematic editorial design, the platform establishes strong visual confidence through scale, high contrast, industrial typography, dark charcoal surfaces, and controlled amber accents without decorative clutter or SaaS templates.

---

## 1. Visual Foundation & Design System

### 1.1 Typography Hierarchy
- **Display & Hero Headings**: `Barlow Condensed` (weights 700-900) — delivers bold, compressed, commanding industrial headers.
- **Body & Controls**: `IBM Plex Sans` (weights 400-600) — clean, legible, technical sans-serif.
- **Telemetry & Metadata Values**: `JetBrains Mono` / `Geist Mono` — high-precision monospace readouts for coordinates, cell counts, tonnages, and variances.

### 1.2 Industrial Color Discipline
- **Canvas Base**: Near-black / dark charcoal (`#07090d`, `#0b0e14`, `#0f141f`) with low-reflectance matte finish.
- **Technical Hairlines**: 1px subtle structural dividers (`border-technical`: `rgba(255, 255, 255, 0.07)`).
- **Primary Accent**: Controlled Industrial Amber (`#f59e0b` / `#d97706`).
- **Semantic Status Badges**:
  - `REAL DATA` (Geospatial & Statutory): Emerald (`#10b981`)
  - `REPORTED DATA` (MOIL Corporate Aggregate): Amber (`#f59e0b`)
  - `EXPERIMENTAL` (Exploration Heuristics): Rose (`#f43f5e`)
  - `SIMULATION` (Block-level Pit Physics): Purple (`#a855f7`)
  - `UNAVAILABLE` (Non-Balaghat Geospatial): Slate (`#64748b`)

---

## 2. Page & Component Redesign Walkthrough

### 2.1 Overview Page (`OverviewPage.jsx`)
- **Cinematic Hero**: Full-width high-contrast mining imagery backdrop with dark gradient overlays, featuring massive condensed typography:
  ```
  MINE INTELLIGENCE
  FOR BETTER MINE DECISIONS
  ```
- **Technical Telemetry Strip**: 6-part technical data provenance readout (10 Mines Registry, Sentinel-2A Multispectral, DEM GLO-30 Elevation, MOIL Production Aggregate, Ensemble Exploration Ranking, Discrete-Event Pit Simulation).
- **Dual Editorial Sections**:
  - **Exploration Priority**: 27,720-cell experimental anomaly ranking with method metadata and scientific disclaimer.
  - **Production Reconciliation**: FY16–FY26 corporate trend vs daily pit operational target variance.
- **Active Pit Blocks Telemetry Table**: Real-time pit schedule and equipment availability status.

### 2.2 Digital Mine Command Center (`MapPage.jsx` & `DigitalMineMap.jsx`)
- **Map-Dominant Layout**: Maximized Leaflet canvas viewing area with dark cartographic styling.
- **Docked GIS Command Panel**: Technical layer toggle matrix (Sentinel-2A B12/B8A/B4, Band Ratios, Hillshade Terrain, Geomorphic Edge Anomaly, Ensemble Exploration Priority).
- **Cell Telemetry Inspector**: Precision coordinate readout, anomaly rank breakdown, and rock exposure metrics with hairline technical framing.

### 2.3 Production Intelligence Hub (`ForecastPage.jsx` & `ProductionAnalytics.jsx`)
- **Industrial Operations Report Layout**: Clean corporate aggregate production trend (FY16–FY26) juxtaposed with block-level simulation reconciliation.
- **Monospace Telemetry Cards**: High-density operational metrics (Target, Simulated, Variance, Blasting Delays, Shovel Availability) replacing rounded SaaS cards.

### 2.4 Navigation & App Shell (`AppShell.jsx`)
- **Minimal Editorial Header**: Clean navigation links (`OVERVIEW`, `DIGITAL MINE`, `PRODUCTION`, `ROOT CAUSE`, `ACTIONS`, `SIMULATOR`, `RESOURCES`) with industrial amber active indicators.
- **Live Telemetry Context Ticker**: Real-time context pill showing current active mine (`MINE: BALAGHAT`), scope level (`BLOCK`), horizon (`30D`), and execution engine status.

---

## 3. Scientific & Data Integrity Safeguards
- **Zero Banned Terms**: Fully audited against prohibited terms (`mineralization probability`, `ore probability`, `reserve probability`, `ore likelihood`, `confirmed ore zone`, `mineralized zone`, `geoproduction ai`).
- **Zero Provenance Bleed**: Real geospatial data, reported corporate statistics, and synthetic block simulations remain strictly segregated with explicit technical badges.
- **Zero ML/Backend Changes**: All ML models, feature rasters (154×180 = 27,720 cells), PuLP optimization algorithms, and FastAPI endpoints are preserved untouched.

---

## 4. Verification Results
- **Pytest Test Suite**: `85 passed, 0 failed, 55 warnings` in 30.47s (100% pass rate).
- **Frontend Build**: `vite build` completed successfully with 0 errors in 2.10s.
- **Git Status**: No Git commits made.
