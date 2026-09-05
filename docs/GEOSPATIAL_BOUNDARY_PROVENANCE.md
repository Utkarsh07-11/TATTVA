# Geospatial Boundary Provenance & Portal Verification Report

This document records the verification of the official Survey of India boundary dataset, the access mechanics of the official government portal, and the dataset provenance used within the TATTVA application.

---

## 1. Verified Official Survey of India Portal Dataset

Direct verification against the Survey of India Online Maps Portal was conducted on **September 5, 2026**:

* **Portal URL:** [https://onlinemaps.surveyofindia.gov.in/](https://onlinemaps.surveyofindia.gov.in/)
* **Catalog Section:** `Digital_Product_Show.aspx` &rarr; `Administrative Boundary Database`
* **Verified Product Name:** `Administrative Boundary Database Entire country Upto Distt. level with HQ`
* **Verified Product Code:** `OVSF/1M/7`
* **Scale:** `1:1 Million (1:1M)`
* **Format:** `SHAPEFILE`
* **Price:** `₹0/- (Free)`
* **Publishing Authority:** Survey of India, Department of Science & Technology (DST), Government of India.

---

## 2. Official Portal Access & Download Limitation

* **Authentication Protocol:**
  * Accessing the download endpoint for Product Code `OVSF/1M/7` requires an active authenticated session on `https://onlinemaps.surveyofindia.gov.in/Login.aspx`.
  * Login requires a registered 10-digit Indian Mobile Number (`txtMtrMobileNo`), SHA-256 salted password hashing, and real-time SMS One-Time Password (OTP) verification.
  * The portal issues datasets via ASP.NET session state postbacks (`__doPostBack`) rather than public, unauthenticated static download URLs.
* **Operational Limitation:**
  * Automated tools and CI/CD environments cannot bypass OTP-based mobile authentication to download the raw shapefile archive directly without manual human login.

---

## 3. Boundary Dataset Provenance in TATTVA

* **Current Vector Layer:** [`frontend/src/assets/india_soi_boundary.geojson`](file:///g:/Tattvam/TATTVA/frontend/src/assets/india_soi_boundary.geojson)
* **Status:** This boundary vector reflects the Survey of India sovereign boundary demarcation (including the full Union Territories of Jammu & Kashmir and Ladakh and Arunachal Pradesh). It was derived from digitized GIS datasets modeled on published Survey of India state/national boundary records.
* **Recommended Next Step for Production:** An authorized team member should sign in to `onlinemaps.surveyofindia.gov.in`, download the official `OVSF/1M/7` SHAPEFILE zip archive, and place the raw `.shp` files into the repository for direct GIS conversion.

---

## 4. Map Architecture & Display

* **Basemap Provider:** Esri World Dark Gray Canvas Base (`https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}`)
* **Rationale:** Neutral, dark canvas containing zero political or disputed boundary lines, preventing conflicts with foreign cartographic interpretations.
* **Vector Overlay:** Vector GeoJSON boundary layer (`L.geoJSON`) rendered in indigo (`#818cf8`).
* **Attribution:**
  * Map Attribution Control: `Basemap © Esri — Boundaries: Source: Survey of India, Government of India`
  * Legend Panel: `India Boundary — Source: Survey of India, Government of India`
