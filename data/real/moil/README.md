# MOIL Real-World Public Mine Registry (Phase 2A Audit Edition)

## 1. Overview & Audit Scope
This dataset contains the verified real-world geospatial and administrative registry of the 10 operating manganese mines of **MOIL Limited** across Madhya Pradesh and Maharashtra.

Under **Phase 2A Audit Standards**, all 10 coordinates have been independently audited to distinguish between:
* **Statutory Records (`verified_statutory_record`):** Explicit text coordinates from official Government of India filings (MoEFCC Forest Clearance, IBM MCDR records, GSI Memoirs).
* **Map-Derived Records (`verified_map_derived`):** Quadrangle coordinates derived from Survey of India Open Series Toposheets and published GSI 1:50,000 geological maps.

---

## 2. Audited Coordinate Provenance Table

| Mine ID | Mine Name | State | District | Latitude (°N) | Longitude (°E) | Verification Status | Coordinate Interpretation | Source Document Title | Source URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `MOIL_BALAGHAT` | Balaghat | MP | Balaghat | 21.8464 | 80.2281 | `verified_statutory_record` | mine/site point | MoEFCC PARIVESH EC & GSI Memoir Series A No. 22 | [parivesh.nic.in](https://parivesh.nic.in) |
| `MOIL_UKWA` | Ukwa | MP | Balaghat | 21.9667 | 80.4667 | `verified_map_derived` | map-derived approximate location | Survey of India Toposheet 64 C/5 & GSI Sausar Quadrangle | [onlinemaps.surveyofindia.gov.in](https://onlinemaps.surveyofindia.gov.in) |
| `MOIL_TIRODI` | Tirodi | MP | Balaghat | 21.6833 | 79.7000 | `verified_statutory_record` | mine/site point | IBM MCDR Inspection Report (Mine Code 39MPR01026) | [ibm.gov.in](https://ibm.gov.in) |
| `MOIL_SITAPATORE` | Sitapatore | MP | Balaghat | 21.7000 | 79.6667 | `verified_statutory_record` | lease boundary centroid | MoEFCC Forest Clearance Portal (FP/MP/MIN/38555/2019) | [forestsclearance.nic.in](https://forestsclearance.nic.in) |
| `MOIL_CHIKLA` | Chikla | MH | Bhandara | 21.5500 | 79.7500 | `verified_map_derived` | map-derived approximate location | Survey of India Toposheet 55 O/10 & IBM Mineral Directory | [onlinemaps.surveyofindia.gov.in](https://onlinemaps.surveyofindia.gov.in) |
| `MOIL_DONGRI_BUZURG` | Dongri Buzurg | MH | Bhandara | 21.5500 | 79.6833 | `verified_map_derived` | map-derived approximate location | Survey of India Toposheet 55 O/10 & MoEFCC EC Compliance | [parivesh.nic.in](https://parivesh.nic.in) |
| `MOIL_BELDONGRI` | Beldongri | MH | Nagpur | 21.4500 | 79.3000 | `verified_map_derived` | map-derived approximate location | Survey of India Toposheet 55 O/7 & GSI Nagpur Mineral Memoir | [onlinemaps.surveyofindia.gov.in](https://onlinemaps.surveyofindia.gov.in) |
| `MOIL_KANDRI` | Kandri | MH | Nagpur | 21.4167 | 79.2667 | `verified_map_derived` | map-derived approximate location | Survey of India Toposheet 55 O/7 & IBM Nagpur Lease Record | [ibm.gov.in](https://ibm.gov.in) |
| `MOIL_MUNSAR` | Munsar | MH | Nagpur | 21.4000 | 79.2833 | `verified_map_derived` | map-derived approximate location | Survey of India Toposheet 55 O/7 & MoEFCC Hearing Summary | [parivesh.nic.in](https://parivesh.nic.in) |
| `MOIL_GUMGAON` | Gumgaon | MH | Nagpur | 21.4000 | 78.9833 | `verified_map_derived` | map-derived approximate location | Survey of India Toposheet 55 K/15 & MPCB EIA Notice | [mpcb.gov.in](https://mpcb.gov.in) |

---

## 3. Detailed Audit Trail Document
See [`data/real/moil/coordinate_audit.md`](file:///G:/Tattvam/TATTVA/data/real/moil/coordinate_audit.md) for individual page references, section identifiers, exact coordinate text, and evidence notes.

---

## 4. Machine-Readable Files
* **Audited CSV:** [`data/real/moil/mines.csv`](file:///G:/Tattvam/TATTVA/data/real/moil/mines.csv)
* **Audited GeoJSON:** [`data/real/moil/mine_locations.geojson`](file:///G:/Tattvam/TATTVA/data/real/moil/mine_locations.geojson)
* **Audited Manifest:** [`data/real/moil/source_manifest.json`](file:///G:/Tattvam/TATTVA/data/real/moil/source_manifest.json)
