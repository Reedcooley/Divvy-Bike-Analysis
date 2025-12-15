"""
Divvy/Bikeshare Data Enrichment Script (v3)
-------------------------------------------
Description:
    Processes CSV to add:
    - ride_time (H:MM:SS)
    - Weekday / Commute flags
    - net_ride_distance_km
    - speed_kmh (New!)
"""

import pandas as pd
import numpy as np
import os

# --- CONFIGURATION ---
input_file = 'processed-data/0-processed_ride_data.csv'
output_file = 'processed-data/0-processed_ride_data_with_speed.csv'

def format_duration(td):
    """Formats timedelta to H:MM:SS"""
    total_seconds = int(round(td.total_seconds()))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours}:{minutes:02d}:{seconds:02d}"

print(f"--- Starting Script ---")

if not os.path.exists(input_file):
    print(f"ERROR: '{input_file}' not found.")
else:
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} rows.")

    # 1. Convert timestamps
    # Using 'mixed' format to be safe, though your data looks consistent
    df['started_at'] = pd.to_datetime(df['started_at'], format='mixed')
    df['ended_at'] = pd.to_datetime(df['ended_at'], format='mixed')

    # 2. Calculate Duration
    temp_duration = df['ended_at'] - df['started_at']
    
    # Format as H:MM:SS string
    df['ride_time'] = temp_duration.apply(format_duration)

    # 3. Extract times
    df['start_time'] = df['started_at'].dt.time
    df['end_time'] = df['ended_at'].dt.time

    # 4. Weekday & Commute Logic
    df['Weekday'] = df['started_at'].dt.dayofweek < 5
    
    start_hour = df['started_at'].dt.hour
    duration_seconds = temp_duration.dt.total_seconds()
    
    is_weekday      = df['Weekday'] == True
    is_morning_rush = (start_hour >= 6) & (start_hour < 10)
    is_evening_rush = (start_hour >= 17) & (start_hour < 20)
    is_short_ride   = duration_seconds < 3600
    
    df['commut'] = (is_morning_rush | is_evening_rush) & is_short_ride & is_weekday

    # 5. Net Distance (Haversine)
    def haversine_vectorized(lat1, lon1, lat2, lon2):
        R = 6371.0 
        phi1, phi2 = np.radians(lat1), np.radians(lat2)
        dphi = np.radians(lat2 - lat1)
        dlambda = np.radians(lon2 - lon1)
        a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return R * c

    df['net_ride_distance_km'] = haversine_vectorized(
        df['start_lat'], df['start_lng'], 
        df['end_lat'], df['end_lng']
    )

    # 6. Speed Calculation (km/h) -- NEW
    # Avoid division by zero: replace 0 hours with NaN temporarily
    duration_hours = duration_seconds / 3600
    df['speed_kmh'] = df['net_ride_distance_km'] / duration_hours.replace(0, np.nan)
    
    # Fill NaN speeds (caused by 0 duration) with 0
    df['speed_kmh'] = df['speed_kmh'].fillna(0)

    # 7. Save
    df.to_csv(output_file, index=False)
    print(f"--- Done! Saved to '{output_file}' ---")