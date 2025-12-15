"""
Divvy/Bikeshare Data Enrichment Script

Description:
    This script processes raw bikeshare trip data (CSV format) to add 
    temporal and spatial features for analysis. It calculates ride duration, 
    extracts time components, determines if a trip occurred on a weekday, 
    flags potential commute trips, and calculates the net displacement distance.

Input:
    - CSV file containing: ride_id, started_at, ended_at, start_lat, 
      start_lng, end_lat, end_lng, etc.

Output:
    - A new CSV file with the following added columns:
      1. ride_time: Duration of the ride.
      2. start_time / end_time: Time components extracted from timestamps.
      3. Weekday: Boolean (True if Mon-Fri, False if Sat-Sun).
      4. commut: Boolean based on specific rush hour logic:
         - (6am-10am OR 5pm-8pm) AND duration < 1 hour.
      5. net_ride_distance: Haversine (great-circle) distance in km.

Dependencies:
    - pandas
    - numpy
"""

import pandas as pd
import numpy as np
import os

# --- CONFIGURATION ---
input_file = 'processed-data/0-combined_output.csv'
output_file = 'processed-data/0-processed_ride_data.csv'

def format_duration(td):
    """
    Converts a timedelta to a string string "H:MM:SS" 
    where H can exceed 24 hours.
    """
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
    df['started_at'] = pd.to_datetime(df['started_at'])
    df['ended_at'] = pd.to_datetime(df['ended_at'])

    # 2. Calculate raw duration (needed for logic)
    # We keep a temporary column for calculations
    temp_duration = df['ended_at'] - df['started_at']

    # 3. Create formatted 'ride_time' (H:MM:SS)
    print("Formatting ride times (Hours:Minutes:Seconds)...")
    # Apply the helper function to every row
    df['ride_time'] = temp_duration.apply(format_duration)

    # 4. Extract times
    df['start_time'] = df['started_at'].dt.time
    df['end_time'] = df['ended_at'].dt.time

    # 5. Weekday Boolean
    # Monday=0 ... Friday=4, Saturday=5, Sunday=6
    df['Weekday'] = df['started_at'].dt.dayofweek < 5

    # 6. Commute Boolean (Updated Logic)
    print("Identifying commute trips (Weekdays only)...")
    
    start_hour = df['started_at'].dt.hour
    duration_seconds = temp_duration.dt.total_seconds()
    
    # Logic definitions
    is_weekday      = df['Weekday'] == True
    is_morning_rush = (start_hour >= 6) & (start_hour < 10)
    is_evening_rush = (start_hour >= 17) & (start_hour < 20)
    is_short_ride   = duration_seconds < 3600
    
    # Combine: (Morning OR Evening) AND Short AND Weekday
    df['commut'] = (is_morning_rush | is_evening_rush) & is_short_ride & is_weekday

    # 7. Calculate Net Distance (Haversine)
    print("Calculating distances...")
    def haversine_vectorized(lat1, lon1, lat2, lon2):
        R = 6371.0 # km
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

    # 8. Save
    df.to_csv(output_file, index=False)
    print(f"--- Done! Saved to '{output_file}' ---")