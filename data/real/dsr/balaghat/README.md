# Balaghat District Survey Report (DSR 2022) Integration Dataset

**Source Authority:** Directorate of Geology and Mining, Government of Madhya Pradesh & District Collectorate Balaghat  
**Publication:** District Survey Report of Balaghat District (2022)  
**Target Region:** Central India Manganese Belt (Balaghat District, Madhya Pradesh)  
**Data Classification:** `SOURCE-DERIVED` / `REAL`  
**Audit Version:** Phase 15.1 (Data Provenance + Lease Geometry Correction Audit)  
**License / Legal Status:** Official Government Statutory Publication (Public Record)

---

## 1. Scope and Contents

This directory contains structured, source-derived datasets extracted directly from the Balaghat District Survey Report (DSR 2022) and cross-referenced with Indian Bureau of Mines (IBM) MCDR mining plan reviews and MoEFCC Environmental Clearance filings:

1. `mine_registry.csv`: Statutory mining leases in Balaghat district (Bharweli, Ukwa, Tirodi, Sitapatore/Sukli, Ramrama, Miragpur) with Tehsil, Village, Khasra, Area (Ha), Mining Method, point coordinate classifications (`point_type`), and strict `provenance_category` (`REAL / SURVEYED`, `SOURCE-DERIVED`, `REFERENCE`).
2. `lease_areas.csv`: Forest vs Non-forest lease breakdown, lease validity periods, statutory clearance numbers, and fully documented area discrepancy reconciliation (Ukwa: 199.07 Ha core grant vs 247.63 Ha consolidated operational leasehold vs 272.634 Ha historical application; Bharweli: 180.44 Ha).
3. `boundary_pillars.csv`: Audited statutory survey and reference points in WGS84 and projected UTM Zone 44N metric coordinates with explicit `point_type` and provenance.
4. `boundaries.geojson`: FeatureCollection of validated statutory reference points (`shaft_portal`, `lease_centroid`, `mine_site_reference`). Complete boundary polygons are explicitly classified as `UNAVAILABLE` because full closed boundary vector cadastre is unreleased in public domain statutory texts.
5. `geology_reference.csv`: Sausar Group stratigraphic formations (Bichua, Junewani, Chorbaoli, Mansar, Lohangi, Sitasaongi, Tirodi Gneiss), lithology, and manganese ore bed characteristics. Maintained purely as structured reference without fabricating unverified spatial polygons.
6. `grade_reference.csv`: Chemical assay distributions (% Mn, % Fe, % SiO2, % P) by deposit and grade category. Kept strictly as statistical distributions without fabricating synthetic drillhole collars.
7. `exploration_evidence.csv`: Aggregate borehole counts, meterage drilled, and UNFC reserve/resource classifications.
8. `production_reference.csv`: District-level reported production and mine-level reported figures tagged strictly by `production_status` (`reported_actual`, `reported_aggregate`).
9. `mine_plan_targets.csv`: Approved five-year planned production targets (strictly isolated from actual production).
10. `constraints.csv`: Engineering, environmental, and operational constraints (bench heights, stowing ratios, beneficiation recovery %, water discharge limits).

---

## 2. Provenance & Geometry Correction Rules (Phase 15.1)

- **No Fabricated Polygons**: Manually constructed approximate 10-vertex polygons were removed in Phase 15.1. Boundary polygons remain classified as `UNAVAILABLE` until authoritative vector cadastre is officially published.
- **Multiple Spatial Reference Types**: Mines are tagged with `point_type` (`shaft_portal`, `lease_centroid`, `mine_site_reference`, `outcrop_strike_center`, `boundary_centroid`) to prevent coordinate collision.
- **Projected Metric CRS**: Geodetic calculations utilize UTM Zone 44N (EPSG:32644) metric projection rather than rough degree-to-meter approximations.
- **Strict Area Reconciliation**: All reported area figures (Bharweli 180.44 Ha, Ukwa 199.07 Ha / 247.63 Ha / 272.634 Ha, Tirodi 165.73 Ha / 214.20 Ha, Sitapatore 43.353 Ha) are mapped to their specific statutory grant, forest/non-forest, or operational definitions.
- **No Synthetic Assay Collars**: Aggregate borehole counts remain exploration evidence; no individual synthetic drillhole collars (BH001, etc.) are generated from aggregate statistics.
