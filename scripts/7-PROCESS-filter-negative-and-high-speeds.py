"""
Divvy Data Enrichment & Cleaning Script (Final)
-----------------------------------------------
Thresholds:
1. Speed Limit: 32 km/h (Based on 99th percentile = 26 km/h)
2. Duration: Must be positive (removes negative timestamps)
3. Magic Travel: Removes rows with Distance > 0 but Time = 0
4. Commute Logic: Now excludes trips with 0 distance (Round trips)
"""

import pandas as pd
import numpy as np
import os

input_file = 'processed-data/0-processed_ride_data_with_speed.csv'
output_file = 'processed-data/0-processed_ride_data_with_speed_cleaned.csv'

# STRICT THRESHOLD (Safe because 99% of data is < 26.2 km/h)
SPEED_THRESHOLD_KMH = 32.0 

def format_duration(td):
    total_seconds = int(round(td.total_seconds()))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours}:{minutes:02d}:{seconds:02d}"

print(f"--- Starting Final Process ---")

if os.path.exists(input_file):
    df = pd.read_csv(input_file)
    original_count = len(df)
    
    # 1. Flexible Timestamp Conversion
    df['started_at'] = pd.to_datetime(df['started_at'], format='mixed')
    df['ended_at'] = pd.to_datetime(df['ended_at'], format='mixed')

    # 2. Calculate Distance & Duration
    temp_duration = df['ended_at'] - df['started_at']
    duration_seconds = temp_duration.dt.total_seconds()
    
    # Haversine Distance
    def haversine_vectorized(lat1, lon1, lat2, lon2):
        R = 6371.0 
        phi1, phi2 = np.radians(lat1), np.radians(lat2)
        dphi = np.radians(lat2 - lat1)
        dlambda = np.radians(lon2 - lon1)
        a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return R * c

    df['net_ride_distance_km'] = haversine_vectorized(
        df['start_lat'], df['start_lng'], df['end_lat'], df['end_lng']
    )

    # 3. Calculate Speed
    # Use epsilon to avoid DivisionByZero errors, but we handle 0 duration later anyway
    duration_hours = duration_seconds / 3600
    df['speed_kmh'] = df['net_ride_distance_km'] / duration_hours.replace(0, np.nan)
    
    # --- FILTERING ---
    print("Applying filters...")
    
    # Filter A: Negative Duration (Fixes the -42 km/h min speed)
    mask_negative = duration_seconds < 0
    
    # Filter B: Magic Travel (Distance > 0, Time = 0)
    mask_magic = (df['net_ride_distance_km'] > 0.01) & (duration_seconds == 0)
    
    # Filter C: Speeders (> 32 km/h)
    # We use fillna(0) for the check so NaNs don't break the boolean logic
    mask_speeders = (df['speed_kmh'].fillna(0) > SPEED_THRESHOLD_KMH)
    
    # Combine Filters (Drop if A or B or C is True)
    rows_to_drop = mask_negative | mask_magic | mask_speeders
    df_clean = df[~rows_to_drop].copy()
    
    # --- FINAL ENRICHMENT ---
    
    # Re-calc ride_time formatting on clean data
    df_clean['ride_time'] = (df_clean['ended_at'] - df_clean['started_at']).apply(format_duration)
    
    # Extract Times
    df_clean['start_time'] = df_clean['started_at'].dt.time
    df_clean['end_time'] = df_clean['ended_at'].dt.time
    
    # Weekday & Commute Logic
    df_clean['Weekday'] = df_clean['started_at'].dt.dayofweek < 5
    
    start_hour = df_clean['started_at'].dt.hour
    is_weekday = df_clean['Weekday'] == True
    is_morning = (start_hour >= 6) & (start_hour < 10)
    is_evening = (start_hour >= 17) & (start_hour < 20)
    
    clean_duration = (df_clean['ended_at'] - df_clean['started_at']).dt.total_seconds()
    is_short   = clean_duration < 3600

    # NEW CONDITION: Distance must be > 0 (excludes Round Trips)
    is_not_round_trip = df_clean['net_ride_distance_km'] > 0
    
    df_clean['commut'] = (is_morning | is_evening) & is_short & is_weekday & is_not_round_trip
    
    # Fill NaN speeds with 0 for cleaner file
    df_clean['speed_kmh'] = df_clean['speed_kmh'].fillna(0)

    # Save
    df_clean.to_csv(output_file, index=False)
    
    print(f"\n--- Summary ---")
    print(f"Original Rows: {original_count}")
    print(f"Dropped Rows:  {original_count - len(df_clean)}")
    print(f"Final Rows:    {len(df_clean)}")
    print(f"Saved to:      {output_file}")