"""
Synthetic Data Generation Engine for SIH 2026 PS 26009
Generates realistic mining, geological, operational, equipment, and satellite proxy data
representing the Central Indian Manganese Belt (Sausar Belt / Nagpur-Balaghat district).
All synthetic datasets are tagged with 'synthetic: true'.
"""

import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd

from config.settings import settings


# Set seeds for deterministic generation
np.random.seed(42)
random.seed(42)

def generate_production_daily() -> pd.DataFrame:
    """
    Generates multi-year daily production logs across 3 mine blocks:
    BLOCK_A (Primary high-grade pit), BLOCK_B (Active bench), BLOCK_C (Developing pit).
    Models weather penalties, equipment availability, and blasting delay cadence.
    """
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2026, 8, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    
    blocks = ["BLOCK_A", "BLOCK_B", "BLOCK_C"]
    base_capacities = {
        "BLOCK_A": 333.3,  # ~10,000 tonnes/month
        "BLOCK_B": 280.0,  # ~8,400 tonnes/month
        "BLOCK_C": 220.0,  # ~6,600 tonnes/month
    }
    
    rows = []
    
    for current_date in date_range:
        day_of_year = current_date.timetuple().tm_yday
        is_monsoon = 160 <= day_of_year <= 270  # June to September in Central India
        
        # Weather generation
        if is_monsoon:
            rainfall_prob = 0.45
            rainfall_mm = max(0.0, float(np.random.exponential(scale=18.0))) if np.random.rand() < rainfall_prob else 0.0
        else:
            rainfall_prob = 0.08
            rainfall_mm = max(0.0, float(np.random.exponential(scale=4.0))) if np.random.rand() < rainfall_prob else 0.0
            
        for block in blocks:
            base_rate = base_capacities[block]
            planned_tonnes = round(base_rate * np.random.uniform(0.95, 1.05), 1)
            
            # Baseline availability fluctuates between 70% and 95%
            availability = float(np.clip(np.random.normal(loc=83.0, scale=8.0), 50.0, 98.0))
            
            # Monsoon impacts availability
            if rainfall_mm > 30.0:
                availability = max(40.0, availability - np.random.uniform(15.0, 30.0))
            
            # Blasting delays happen due to heavy rain, safety clearance, or misfire
            blast_delay_prob = 0.05 + (0.35 if rainfall_mm > 20.0 else 0.0)
            blasting_delay_flag = int(np.random.rand() < blast_delay_prob)
            
            # Maintenance flag (scheduled periodic PM or unscheduled breakdowns)
            maintenance_prob = 0.08 if availability < 75.0 else 0.03
            maintenance_flag = int(np.random.rand() < maintenance_prob)
            
            # Scenario simulation alignment for recent month in BLOCK_A (Section 18 scenario):
            # Monthly target: 10,000 tonnes, forecast ~8,650 tonnes due to maintenance & blast delay & rain
            if block == "BLOCK_A" and (end_date - current_date).days <= 30:
                # Force realistic shortfall conditions matching Section 18
                availability = float(np.clip(np.random.normal(loc=72.0, scale=5.0), 60.0, 85.0))
                if (end_date - current_date).days in [5, 6, 12, 13]:
                    maintenance_flag = 1  # 4 days maintenance
                if (end_date - current_date).days in [8, 21]:
                    blasting_delay_flag = 1  # 2 blasting delays
                if (end_date - current_date).days in [15, 16, 17, 18, 19, 20]:
                    rainfall_mm = float(np.random.uniform(5.0, 12.0))
            
            # Production formulation:
            # production = base_rate * (avail / 100) * (1 - weather_penalty) * (1 - blast_penalty) + noise
            rain_penalty = min(0.35, 0.012 * rainfall_mm)
            blast_penalty = 0.28 if blasting_delay_flag else 0.0
            maint_penalty = 0.22 if maintenance_flag else 0.0
            
            efficiency = (availability / 100.0) * (1.0 - rain_penalty) * (1.0 - blast_penalty) * (1.0 - maint_penalty)
            noise = float(np.random.normal(0, 10.0))
            actual_tonnes = max(0.0, round(base_rate * efficiency + noise, 1))
            
            rows.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "mine_block_id": block,
                "planned_tonnes": planned_tonnes,
                "actual_tonnes": actual_tonnes,
                "equipment_availability_pct": round(availability, 1),
                "rainfall_mm": round(rainfall_mm, 1),
                "blasting_delay_flag": blasting_delay_flag,
                "maintenance_flag": maintenance_flag,
                "synthetic": True,
            })
            
    df = pd.DataFrame(rows)
    return df


def generate_equipment_events() -> pd.DataFrame:
    """
    Generates discrete equipment events (downtime, repairs, PM) using Weibull failure times.
    """
    equipments = [
        ("EXC-01", "BLOCK_A", "Excavator 120T"),
        ("EXC-02", "BLOCK_A", "Excavator 85T"),
        ("EXC-03", "BLOCK_A", "Excavator 85T"),
        ("EXC-04", "BLOCK_B", "Excavator 120T"),
        ("EXC-05", "BLOCK_B", "Excavator 85T"),
        ("EXC-06", "BLOCK_C", "Excavator 85T"),
        ("DMP-01", "BLOCK_A", "Dumper 60T"),
        ("DMP-02", "BLOCK_A", "Dumper 60T"),
        ("DMP-03", "BLOCK_A", "Dumper 60T"),
        ("DMP-04", "BLOCK_A", "Dumper 60T"),
        ("DMP-05", "BLOCK_B", "Dumper 60T"),
        ("DMP-06", "BLOCK_B", "Dumper 60T"),
        ("DMP-07", "BLOCK_B", "Dumper 60T"),
        ("DMP-08", "BLOCK_B", "Dumper 60T"),
        ("DMP-09", "BLOCK_C", "Dumper 60T"),
        ("DMP-10", "BLOCK_C", "Dumper 60T"),
        ("DRL-01", "BLOCK_A", "Rotary Drill 150mm"),
        ("DRL-02", "BLOCK_A", "Rotary Drill 150mm"),
        ("DRL-03", "BLOCK_B", "Rotary Drill 150mm"),
        ("DRL-04", "BLOCK_C", "Rotary Drill 150mm"),
    ]
    
    event_types = ["downtime", "maintenance", "repair"]
    causes = [
        ("HYDRAULIC_LEAK", "Hydraulic seal rupture on main boom"),
        ("ENGINE_OVERHEAT", "Coolant pump failure during high ambient temp"),
        ("TRACK_DAMAGE", "Track shoe displacement on haulage floor"),
        ("ELECTRICAL_FAULT", "Alternator circuit grounding issue"),
        ("SCHEDULED_PM", "250-hour routine preventive maintenance inspection"),
        ("BLAST_VIBRATION_CHECK", "Safety inspection after bench blast"),
        ("TIRE_WEAR", "Severe tire gouging from jagged gondite boulders"),
    ]
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 8, 31)
    
    events = []
    event_id = 1001
    
    for eq_id, block, model in equipments:
        curr_time = start_date + timedelta(hours=random.randint(12, 96))
        while curr_time < end_date:
            # Weibull time between events (MTBF)
            hours_to_next = float(np.random.weibull(a=1.8) * 160.0 + 24.0)
            curr_time += timedelta(hours=hours_to_next)
            if curr_time >= end_date:
                break
                
            event_type = random.choices(event_types, weights=[0.45, 0.35, 0.20])[0]
            cause_code, desc = random.choice(causes)
            duration_hours = round(float(np.random.lognormal(mean=1.5, sigma=0.6)), 1)
            duration_hours = max(1.0, min(72.0, duration_hours))
            
            end_time = curr_time + timedelta(hours=duration_hours)
            
            events.append({
                "event_id": f"EVT-{event_id}",
                "equipment_id": eq_id,
                "equipment_model": model,
                "mine_block_id": block,
                "event_type": event_type,
                "start_time": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_hours": duration_hours,
                "cause_code": cause_code,
                "description": desc,
                "synthetic": True,
            })
            event_id += 1
            curr_time = end_time
            
    df = pd.DataFrame(events)
    return df


def generate_drillhole_assay() -> pd.DataFrame:
    """
    Generates 240 georeferenced drillholes with assay records.
    Coordinates match the Balaghat / Ukwa / Bharweli manganese belt in Madhya Pradesh / Maharashtra.
    Lithologies reflect Sausar Group: Mansar Formation, Gondite, Quartzite, Tirodi Biotite Gneiss.
    """
    center_lat = settings.CENTER_LAT
    center_lon = settings.CENTER_LON
    
    lithologies = [
        ("MANSAR_SCHIST", 0.30, 22.0, 38.0),   # high grade Mn host rock
        ("GONDITE", 0.35, 14.0, 32.0),         # manganiferous quartzite / gondite ore
        ("QUARTZITE", 0.15, 1.5, 8.0),          # barren / low grade wall rock
        ("CALC_GRANULITE", 0.10, 0.5, 4.0),     # footwall rock
        ("TIRODI_GNEISS", 0.10, 0.2, 2.0),      # basement rock
    ]
    
    # We create 3 spatial clusters representing known synclinal fold axes
    clusters = [
        (center_lat - 0.008, center_lon - 0.010, "Syncline_Axis_West", 0.65),
        (center_lat + 0.005, center_lon + 0.006, "Main_Lode_Central", 0.85),
        (center_lat + 0.012, center_lon - 0.004, "Northern_Limb", 0.40),
    ]
    
    rows = []
    hole_counter = 1
    
    for cluster_lat, cluster_lon, cluster_name, ore_prior in clusters:
        num_holes = 80
        for _ in range(num_holes):
            # Spatial distribution around fold axis
            lat = cluster_lat + np.random.normal(0, 0.004)
            lon = cluster_lon + np.random.normal(0, 0.005)
            
            # Collar elevation
            collar_elevation = round(380.0 + np.random.uniform(-25.0, 45.0), 1)
            total_depth = round(random.uniform(45.0, 180.0), 1)
            
            # Ore bearing probability decays with distance from cluster center
            dist = np.sqrt((lat - cluster_lat)**2 + (lon - cluster_lon)**2)
            prob_ore = ore_prior * np.exp(-dist / 0.006)
            is_ore = np.random.rand() < prob_ore
            
            if is_ore:
                lith_name, _, min_mn, max_mn = random.choice([lithologies[0], lithologies[1]])
                mn_grade = round(float(np.random.uniform(min_mn, max_mn)), 2)
                fe_grade = round(float(np.random.uniform(4.0, 11.0)), 2)
                sio2_grade = round(float(np.random.uniform(12.0, 32.0)), 2)
                depth_from = round(random.uniform(10.0, total_depth - 15.0), 1)
                thickness = round(random.uniform(2.5, 14.0), 1)
                depth_to = round(depth_from + thickness, 1)
            else:
                lith_choice = random.choice([lithologies[2], lithologies[3], lithologies[4]])
                lith_name, _, min_mn, max_mn = lith_choice
                mn_grade = round(float(np.random.uniform(min_mn, max_mn)), 2)
                fe_grade = round(float(np.random.uniform(2.0, 7.0)), 2)
                sio2_grade = round(float(np.random.uniform(45.0, 78.0)), 2)
                depth_from = round(random.uniform(5.0, total_depth - 10.0), 1)
                thickness = round(random.uniform(1.0, 8.0), 1)
                depth_to = round(depth_from + thickness, 1)
                
            sample_date = (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 1100))).strftime("%Y-%m-%d")
            
            rows.append({
                "hole_id": f"DH-{hole_counter:04d}",
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "collar_elevation_m": collar_elevation,
                "total_depth_m": total_depth,
                "depth_from_m": depth_from,
                "depth_to_m": depth_to,
                "thickness_m": thickness,
                "mn_grade_pct": mn_grade,
                "fe_grade_pct": fe_grade,
                "sio2_pct": sio2_grade,
                "lithology_code": lith_name,
                "sample_date": sample_date,
                "structural_domain": cluster_name,
                "is_ore_bearing": int(mn_grade >= 18.0),
                "source": "synthetic",
            })
            hole_counter += 1
            
    df = pd.DataFrame(rows)
    return df


def generate_satellite_features_grid() -> pd.DataFrame:
    """
    Generates a 35x35 spatial grid of satellite-derived optical and terrain proxies
    (Sentinel-2 SWIR/VNIR band ratios, DEM slope/aspect, NDVI, NDWI, LST).
    """
    center_lat = settings.CENTER_LAT
    center_lon = settings.CENTER_LON
    
    grid_size = 35
    lat_span = 0.04
    lon_span = 0.04
    
    lats = np.linspace(center_lat - lat_span/2, center_lat + lat_span/2, grid_size)
    lons = np.linspace(center_lon - lon_span/2, center_lon + lon_span/2, grid_size)
    
    rows = []
    grid_id = 1
    
    for lat in lats:
        for lon in lons:
            # DEM terrain proxies
            dist_to_center = np.sqrt((lat - center_lat)**2 + (lon - center_lon)**2)
            elevation = 360.0 + 80.0 * np.sin(lat * 500) * np.cos(lon * 500) + np.random.normal(0, 3)
            slope = float(np.clip(12.0 + 15.0 * np.sin((lat + lon) * 300) + np.random.normal(0, 2), 1.0, 48.0))
            aspect = float(random.uniform(0.0, 360.0))
            
            # Optical indices:
            # Manganese alteration zones in Central India typically feature gossanous iron oxides,
            # clay mineral alteration, and sparse vegetation stress (lower NDVI, higher iron oxide ratio)
            in_alteration_zone = dist_to_center < 0.012 and (slope > 8.0)
            
            if in_alteration_zone:
                iron_oxide_ratio = float(np.random.normal(loc=2.25, scale=0.25))  # B4/B2 Sentinel-2
                clay_ratio = float(np.random.normal(loc=1.85, scale=0.20))        # B11/B12 Sentinel-2 SWIR
                ferrous_ratio = float(np.random.normal(loc=1.65, scale=0.18))     # B12/B8
                ndvi = float(np.clip(np.random.normal(loc=0.22, scale=0.06), 0.05, 0.45))
                ndwi = float(np.clip(np.random.normal(loc=-0.28, scale=0.08), -0.5, 0.0))
                lst_k = float(np.random.normal(loc=310.5, scale=2.5))  # Higher thermal inertia / surface temp
            else:
                iron_oxide_ratio = float(np.random.normal(loc=1.20, scale=0.20))
                clay_ratio = float(np.random.normal(loc=1.10, scale=0.15))
                ferrous_ratio = float(np.random.normal(loc=1.05, scale=0.15))
                ndvi = float(np.clip(np.random.normal(loc=0.48, scale=0.10), 0.15, 0.85))
                ndwi = float(np.clip(np.random.normal(loc=-0.05, scale=0.10), -0.3, 0.3))
                lst_k = float(np.random.normal(loc=303.0, scale=2.0))
                
            rows.append({
                "grid_id": f"GRID-{grid_id:04d}",
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "elevation_m": round(elevation, 1),
                "slope_deg": round(slope, 1),
                "aspect_deg": round(aspect, 1),
                "ndvi": round(ndvi, 3),
                "ndwi": round(ndwi, 3),
                "iron_oxide_index": round(iron_oxide_ratio, 3),
                "clay_index": round(clay_ratio, 3),
                "ferrous_index": round(ferrous_ratio, 3),
                "lst_k": round(lst_k, 1),
                "acquisition_date": "2026-03-15",
                "synthetic": True,
            })
            grid_id += 1
            
    df = pd.DataFrame(rows)
    return df


def generate_mine_blocks_geojson() -> dict:
    """
    Generates georeferenced GeoJSON polygon boundaries for mine blocks and facilities.
    """
    clat = settings.CENTER_LAT
    clon = settings.CENTER_LON
    
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "block_id": "BLOCK_A",
                    "name": "Main Pit - Block A (High Grade)",
                    "status": "Active Extraction",
                    "target_monthly_tonnes": 10000,
                    "target_mn_grade_pct": 36.5,
                    "primary_equipment": ["EXC-01", "EXC-02", "EXC-03", "DRL-01"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [clon - 0.007, clat + 0.002],
                        [clon - 0.002, clat + 0.008],
                        [clon + 0.004, clat + 0.005],
                        [clon + 0.001, clat - 0.002],
                        [clon - 0.005, clat - 0.001],
                        [clon - 0.007, clat + 0.002],
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "block_id": "BLOCK_B",
                    "name": "East Extension - Block B",
                    "status": "Active Development",
                    "target_monthly_tonnes": 8400,
                    "target_mn_grade_pct": 28.0,
                    "primary_equipment": ["EXC-04", "EXC-05", "DRL-03"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [clon + 0.005, clat + 0.009],
                        [clon + 0.012, clat + 0.012],
                        [clon + 0.014, clat + 0.004],
                        [clon + 0.007, clat + 0.002],
                        [clon + 0.005, clat + 0.009],
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "block_id": "BLOCK_C",
                    "name": "South Overburden Strip - Block C",
                    "status": "Stripping / Secondary",
                    "target_monthly_tonnes": 6600,
                    "target_mn_grade_pct": 22.0,
                    "primary_equipment": ["EXC-06", "DRL-04"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [clon - 0.012, clat - 0.004],
                        [clon - 0.006, clat - 0.003],
                        [clon - 0.004, clat - 0.011],
                        [clon - 0.011, clat - 0.012],
                        [clon - 0.012, clat - 0.004],
                    ]]
                }
            }
        ]
    }
    return geojson


def main():
    print("Generating synthetic datasets for SIH 2026 PS 26009...")
    
    prod_df = generate_production_daily()
    prod_path = settings.SYNTHETIC_DATA_DIR / "production_daily.csv"
    prod_df.to_csv(prod_path, index=False)
    print(f"-> Saved {len(prod_df)} production records to {prod_path}")
    
    eq_df = generate_equipment_events()
    eq_path = settings.SYNTHETIC_DATA_DIR / "equipment_events.csv"
    eq_df.to_csv(eq_path, index=False)
    print(f"-> Saved {len(eq_df)} equipment event records to {eq_path}")
    
    dh_df = generate_drillhole_assay()
    dh_path = settings.SYNTHETIC_DATA_DIR / "drillhole_assay.csv"
    dh_df.to_csv(dh_path, index=False)
    print(f"-> Saved {len(dh_df)} drillhole assay records to {dh_path}")
    
    sat_df = generate_satellite_features_grid()
    sat_path = settings.SYNTHETIC_DATA_DIR / "satellite_features_grid.csv"
    sat_df.to_csv(sat_path, index=False)
    print(f"-> Saved {len(sat_df)} satellite grid features to {sat_path}")
    
    geo_json = generate_mine_blocks_geojson()
    geo_path = settings.SYNTHETIC_DATA_DIR / "mine_blocks.geojson"
    with open(geo_path, "w") as f:
        json.dump(geo_json, f, indent=2)
    print(f"-> Saved mine blocks GeoJSON boundary to {geo_path}")
    
    # Also copy a baseline version to processed folder for immediate loading
    prod_df.to_csv(settings.PROCESSED_DATA_DIR / "production_daily.csv", index=False)
    dh_df.to_csv(settings.PROCESSED_DATA_DIR / "drillhole_assay.csv", index=False)
    sat_df.to_csv(settings.PROCESSED_DATA_DIR / "satellite_features_grid.csv", index=False)
    eq_df.to_csv(settings.PROCESSED_DATA_DIR / "equipment_events.csv", index=False)
    with open(settings.PROCESSED_DATA_DIR / "mine_blocks.geojson", "w") as f:
        json.dump(geo_json, f, indent=2)
        
    print("Synthetic data generation successfully completed.")

if __name__ == "__main__":
    main()
