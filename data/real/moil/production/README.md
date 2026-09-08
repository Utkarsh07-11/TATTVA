# Real Historical Production Dataset (MOIL & Central India Manganese Belt)

## 1. Overview & Dataset Scope
This dataset compiles official, publicly reported historical production data for **MOIL Limited** and the **Central India Manganese Belt** (Madhya Pradesh & Maharashtra), acquired under **Phase 6** of Project TATTVA.

All records in this dataset represent **direct statutory observations** extracted from audited MOIL Annual Reports, Ministry of Steel (Government of India) Press Information Bureau (PIB) releases, and Indian Bureau of Mines (IBM) Indian Minerals Yearbooks.

---

## 2. Real vs. Synthetic Production Architecture

| Dimension | Real Reported Data (`data/real/moil/production/`) | Synthetic Operational Data (`data/synthetic/production_daily.csv`) |
|---|---|---|
| **Purpose** | Historical baseline, macroeconomic calibration, statutory reporting truth. | Micro-simulation for dispatch scheduling, daily shovel-truck haulage ML modeling. |
| **Temporal Granularity** | Annual, Quarterly, and milestone Monthly totals. | Daily operational shift logs (`2023-01-01` to `2026-08-31`). |
| **Spatial Granularity** | Company-wide aggregate (MOIL 10-mine portfolio) & State/National totals. | Sub-pit mine blocks (`BLOCK_A`, `BLOCK_B`, `BLOCK_C` of Balaghat Mine). |
| **Operational Variables** | Net extracted run-of-mine (ROM) manganese ore tonnage. | Planned vs. actual tonnage, equipment availability %, rainfall mm, blasting delay flag, maintenance flag. |
| **Data Status** | `reported` (100% audited provenance). | `synthetic` (Simulated for ML stress-testing). |

> [!IMPORTANT]
> **Strict Provenance Principle:** In TATTVA, company-level annual reported totals are **NEVER** mathematically divided down into fake daily time-series or assigned arbitrarily to individual mines. Real historical data and synthetic operational data remain strictly separated.

---

## 3. Data Dictionary (`production_reported.csv`)

| Column | Type | Description | Example |
|---|---|---|---|
| `period` | string | Reporting interval identifier | `FY2023-24`, `Q3_FY2024-25`, `2025-08` |
| `period_type` | string | Temporal grain: `annual`, `quarterly`, or `monthly` | `annual` |
| `mine` | string | Mine identifier or aggregate category | `ALL_MINES_AGGREGATE`, `STATE_TOTAL` |
| `company` | string | Operating enterprise | `MOIL Limited`, `ALL_OPERATORS` |
| `state` | string | State or geographical region | `MP_AND_MAH`, `Madhya Pradesh`, `Maharashtra` |
| `commodity` | string | Mineral commodity | `Manganese Ore` |
| `production_tonnes` | float | Total run-of-mine production in Metric Tonnes | `1756000.0` |
| `grade_percent` | float | Average manganese grade percentage if disclosed | `null` |
| `source` | string | Authoritative publication title | `MOIL 62nd Annual Report` |
| `source_page` | string | Document section or page reference | `Directors Report` |
| `source_table` | string | Table or release identifier | `Production Summary Table` |
| `data_status` | string | Verification status (always `reported` for this dataset) | `reported` |

---

## 4. Key Historical Production Highlights

* **11-Year Annual Corporate Series (FY 2015-16 to FY 2025-26):**
  * **FY 2015-16:** $1,032,000 \text{ MT}$ ($10.32 \text{ LMT}$)
  * **FY 2016-17:** $1,005,000 \text{ MT}$ ($10.05 \text{ LMT}$)
  * **FY 2017-18:** $1,201,000 \text{ MT}$ ($12.01 \text{ LMT}$)
  * **FY 2018-19:** $1,301,000 \text{ MT}$ ($13.01 \text{ LMT}$)
  * **FY 2019-20:** $1,280,000 \text{ MT}$ ($12.80 \text{ LMT}$)
  * **FY 2020-21:** $1,143,000 \text{ MT}$ ($11.43 \text{ LMT}$)
  * **FY 2021-22:** $1,231,000 \text{ MT}$ ($12.31 \text{ LMT}$)
  * **FY 2022-23:** $1,302,000 \text{ MT}$ ($13.02 \text{ LMT}$)
  * **FY 2023-24:** $1,756,000 \text{ MT}$ ($17.56 \text{ LMT}$) — Record $+34.87\%$ YoY growth
  * **FY 2024-25:** $1,802,000 \text{ MT}$ ($18.02 \text{ LMT}$)
  * **FY 2025-26:** $1,907,000 \text{ MT}$ ($19.07 \text{ LMT}$) — Highest-ever production in MOIL history
* **Quarterly & Monthly Disclosures:**
  * **Q1 FY 2026-27:** $507,605 \text{ MT}$
  * **Q3 FY 2025-26:** $477,000 \text{ MT}$
  * **Q1 FY 2024-25:** $470,000 \text{ MT}$
  * **Q3 FY 2024-25:** $460,000 \text{ MT}$
  * **November 2025:** $165,000 \text{ MT}$
  * **September 2025:** $152,000 \text{ MT}$
  * **August 2025:** $145,000 \text{ MT}$
* **National & State Context (IBM IMYB 2022):**
  * **All-India Manganese Production:** $2,695,991 \text{ MT}$
  * **Madhya Pradesh:** $849,237 \text{ MT}$ ($31.50\%$ of national total)
  * **Maharashtra:** $727,918 \text{ MT}$ ($27.00\%$ of national total)

---

## 5. Limitations & Unavailable Data

1. **Granular Mine-Wise Daily Logs:** Continuous daily dispatch or haulage logs by individual pit/shaft (e.g. Balaghat Central Shaft vs. Bharweli Opencast pit) are proprietary internal enterprise operational records not published in public annual statutory reports.
2. **Grade Breakdown by Pit:** Commercial grade distribution (e.g., Silico-Manganese Grade $30-35\%$ vs. High Grade Ferromanganese $44-48\%$ vs. Dioxide Ore) is published only in broad marketing bands rather than continuous spatial coordinates.
