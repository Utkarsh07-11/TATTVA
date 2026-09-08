# Phase 6 — Real Historical Production Data Acquisition Report

**Project:** TATTVA — AI/ML Mining Intelligence Platform  
**Target Enterprise:** MOIL Limited (Manganese Ore India Limited)  
**Target Region:** Central India Manganese Belt (Balaghat, MP & Nagpur/Bhandara, Maharashtra)  
**Audit Date:** September 2026  
**Status:** Acquisition Complete — Real Canonical Dataset & Derived Analytics Established  

---

## 1. Sources Investigated

1. **MOIL Limited Official Annual Reports:**
   * 54th to 62nd Annual Reports (FY 2015-16 through FY 2023-24) — Directors' Reports, Operational Performance Reviews, Financial Statements.
   * Portal: `https://moil.nic.in/` / BSE / NSE Corporate Disclosures.
2. **Ministry of Steel / Press Information Bureau (PIB), Government of India:**
   * Official corporate and physical production bulletins for FY 2024-25, FY 2025-26, and early FY 2026-27 quarters.
   * Portal: `https://pib.gov.in/`
3. **Indian Bureau of Mines (IBM), Ministry of Mines:**
   * *Indian Minerals Yearbook (IMYB) — Manganese Ore Chapter* (2021, 2022, 2023 editions) and *Monthly Statistics of Mineral Production (MSMP)*.
   * Portal: `https://ibm.gov.in/`

---

## 2. Sources Successfully Acquired & Integrated

All 7 source documents and official disclosure series were structured and documented in [`source_manifest.json`](file:///G:/Tattvam/TATTVA/data/real/moil/production/source_manifest.json):
* `MOIL_AR_2023_24` (17.56 LMT)
* `MOIL_AR_2022_23` (13.02 LMT)
* `MOIL_AR_2021_22` (12.31 LMT)
* `MOIL_AR_2015_2021_SERIES` (Historical baseline 10.32 to 13.01 LMT)
* `PIB_MIN_STEEL_2025_26` (Record 19.07 LMT annual; 18.02 LMT in FY 2024-25)
* `PIB_QUARTERLY_MONTHLY_SERIES` (Q1 FY27, Q3 FY26, Q1 FY25, Q3 FY25, and monthly peaks)
* `IBM_IMYB_2022_2023` (State-wise MP & Maharashtra and All-India production)

---

## 3. Production Periods Obtained

* **Annual Time-Series (11 consecutive fiscal years):** FY 2015-16 through FY 2025-26.
* **Quarterly Observations (4 quarters):** Q1 FY24-25, Q3 FY24-25, Q3 FY25-26, Q1 FY26-27.
* **Monthly Milestones (3 distinct months):** August 2025, September 2025, November 2025.
* **State & National Annual Data (2 fiscal years):** FY 2020-21, FY 2021-22 (Madhya Pradesh, Maharashtra, All-India).

---

## 4. Granularity & Coverage

* **Company-Level:** Company-wide aggregate production across MOIL's 10 operating mines in Madhya Pradesh and Maharashtra.
* **State-Level:** State aggregates for Madhya Pradesh (Balaghat/Chhindwara districts) and Maharashtra (Nagpur/Bhandara districts).
* **National Level:** All-India total manganese ore output.
* **Mine-Level Public Availability:** Individual pit/shaft continuous daily production logs are proprietary internal ERP records and are **not** published in statutory annual reports. Capacity targets (e.g. Balaghat Mine 300k–800k TPA) are documented textually.

---

## 5. Data Dictionary of Canonical Dataset (`production_reported.csv`)

| Field | Type | Description | Values |
|---|---|---|---|
| `period` | string | Reporting fiscal year, quarter, or calendar month | `FY2023-24`, `Q3_FY2025-26`, `2025-08` |
| `period_type` | string | Grain of observation | `annual`, `quarterly`, `monthly` |
| `mine` | string | Mine or aggregate scope | `ALL_MINES_AGGREGATE`, `STATE_TOTAL`, `ALL_INDIA_TOTAL` |
| `company` | string | Operating entity | `MOIL Limited`, `ALL_OPERATORS` |
| `state` | string | Territorial scope | `MP_AND_MAH`, `Madhya Pradesh`, `Maharashtra`, `India` |
| `commodity` | string | Commodity name | `Manganese Ore` |
| `production_tonnes` | float | Quantity in Metric Tonnes | Range: `145,000.0` to `2,695,991.0` |
| `grade_percent` | float | Grade if disclosed | Empty (`null`) |
| `source` | string | Authoritative citation | MOIL Annual Reports, PIB Disclosures, IBM IMYB |
| `source_page` | string | Document section | Directors Report, Operational Review, Table 4 |
| `source_table` | string | Table name | Production Summary Table, Annual Press Bulletin |
| `data_status` | string | Verification tag | Always `reported` |

---

## 6. Provenance & Unit Standardization

* **Original Units:** Recorded in Lakh Metric Tonnes (LMT), Thousand Tonnes, or Metric Tonnes.
* **Standardized Units in Canonical CSV:** All quantities converted unambiguously into standard **Metric Tonnes (MT)** ($1 \text{ Lakh Tonnes} = 100,000 \text{ Metric Tonnes}$).
* **Original Unit Metadata:** Preserved in `source_manifest.json` for 100% auditability.

---

## 7. Derived Analytics (`data/derived/production/moil_annual_yoy_growth.csv`)

A separate derived analytics dataset was created to track year-over-year production growth across MOIL's 10-year timeline:
* **FY 2016-17:** $-2.62\%$ ($1,005,000 \text{ MT}$)
* **FY 2017-18:** $+19.50\%$ ($1,201,000 \text{ MT}$)
* **FY 2018-19:** $+8.33\%$ ($1,301,000 \text{ MT}$)
* **FY 2019-20:** $-1.61\%$ ($1,280,000 \text{ MT}$)
* **FY 2020-21:** $-10.70\%$ ($1,143,000 \text{ MT}$, COVID-19 lockdown impact)
* **FY 2021-22:** $+7.70\%$ ($1,231,000 \text{ MT}$)
* **FY 2022-23:** $+5.77\%$ ($1,302,000 \text{ MT}$)
* **FY 2023-24:** $+34.87\%$ ($1,756,000 \text{ MT}$, major post-expansion surge)
* **FY 2024-25:** $+2.62\%$ ($1,802,000 \text{ MT}$)
* **FY 2025-26:** $+5.83\%$ ($1,907,000 \text{ MT}$, peak record production)

---

## 8. Relationship to Synthetic Production Data (`production_daily.csv`)

* `data/synthetic/production_daily.csv` simulates daily shift-level operations across 3 sub-blocks (`BLOCK_A`, `BLOCK_B`, `BLOCK_C`) of the Balaghat Mine (~700–850 tonnes/day total $\approx$ 280,000 tonnes/year).
* **Calibration Compatibility:** The synthetic daily scale matches the known rated capacity of the Balaghat underground mine (~300,000 TPA).
* **Architectural Separation:** The synthetic daily observations remain strictly labeled `synthetic=True`, while the reported dataset in `data/real/moil/production/` is tagged `data_status="reported"`.

---

## 9. Quality Verification & Automated Testing

1. **Automated Unit Tests:**
   * Added `test_real_moil_production_reported()` to [`tests/test_data.py`](file:///G:/Tattvam/TATTVA/tests/test_data.py).
   * Verified: File existence, column completeness, non-negative tonnages, uniqueness of (period, mine, company, state) tuples, and source manifest schema.
   * Pytest execution: **9 passed in 0.75s (100% GREEN)**.
2. **Frontend Build Verification:**
   * Executed `npm run build` in `frontend/`.
   * Result: **Vite production build successful (1.90s)** with zero regressions.

---

## 10. Recommended ML & Production Forecasting Usage

1. **Macro Baseline Forecasting:** Train time-series models (e.g. ARIMA / Prophet / LSTM) on the real 11-year reported series (`FY 2015-16` to `FY 2025-26`) to predict quarterly/annual production targets.
2. **Operational Dispatch Optimization:** Use the synthetic daily logs (`production_daily.csv`) for daily shovel-truck dispatching, equipment maintenance downtime simulation, and weather impact modeling.
3. **Hierarchical Reconciliation:** Real reported quarterly figures provide the macro envelope against which micro operational daily shift plans can be reconciled.

---

## 11. Final Verdict

# **B. COMPANY-LEVEL REAL PRODUCTION DATA AVAILABLE**

### Explanation
Authoritative, audited real production data for MOIL Limited was successfully acquired at the **company-wide aggregate level** across 11 consecutive financial years (FY 2015-16 through FY 2025-26), 4 quarterly disclosures, and 3 monthly milestone records, complemented by state-level totals from the Indian Bureau of Mines. Continuous pit-specific daily operational logs are proprietary internal enterprise records, so company totals were preserved without artificial daily interpolation, maintaining absolute provenance integrity in TATTVA.
