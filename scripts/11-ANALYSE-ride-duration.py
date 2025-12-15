import pandas as pd
import numpy as np

# Load the CLEANED file
file_path = 'processed-data/0-processed_ride_data_with_speed_cleaned.csv'
print(f"Loading {file_path}...")
df = pd.read_csv(file_path)

# Convert timestamps
df['started_at'] = pd.to_datetime(df['started_at'])
df['ended_at'] = pd.to_datetime(df['ended_at'])

# --- 1. FILTER: ISOLATE "NON-COMMUTER" HOURS ---
print("\n--- ANALYSIS: DURATION BREAKDOWN (OFF-PEAK) ---")
print("Excluding Weekday Rush Hours (06-10 & 17-20)...")

# Define Commuter Hours (to EXCLUDE)
# Rush Hour = Weekdays (Mon=0 to Fri=4) AND (Hour 6-9 OR Hour 17-19)
# Note: range(6, 10) is 6,7,8,9.
is_weekday = df['started_at'].dt.dayofweek < 5
hour = df['started_at'].dt.hour
is_rush_hour = (hour >= 6) & (hour < 10) | (hour >= 17) & (hour < 20)
is_commute_time = is_weekday & is_rush_hour

# We want the OPPOSITE (Off-Peak)
off_peak_df = df[~is_commute_time].copy()
print(f"Analyzing {len(off_peak_df)} Off-Peak rides.")

# --- 2. BINNING DURATIONS ---
# Calculate duration in minutes
off_peak_df['duration_min'] = (off_peak_df['ended_at'] - off_peak_df['started_at']).dt.total_seconds() / 60

# Define Bins for "Short Hops" vs "Long Rides"
# 0-5 mins: "Micro-Trip" (e.g., to bus stop)
# 5-10 mins: "Quick Errand"
# 10-20 mins: "Standard Trip"
# 20+ mins: "Leisure/Long Commute"
bins = [0, 5, 10, 20, 30, 60, 9999]
labels = ['0-5m', '5-10m', '10-20m', '20-30m', '30-60m', '60m+']

off_peak_df['duration_bin'] = pd.cut(off_peak_df['duration_min'], bins=bins, labels=labels)

# --- 3. CALCULATE PERCENTAGES ---
# Group by User Type and Bin
grouped = off_peak_df.groupby(['member_casual', 'duration_bin'], observed=False).size().reset_index(name='count')

# Calculate percentage within each user group
# We merge total counts back to divide
total_counts = off_peak_df.groupby('member_casual').size().reset_index(name='total')
grouped = grouped.merge(total_counts, on='member_casual')
grouped['percentage'] = (grouped['count'] / grouped['total'] * 100).round(2)

# Pivot for cleaner display
pivot_table = grouped.pivot(index='duration_bin', columns='member_casual', values='percentage')

print("\nPERCENTAGE OF RIDES BY DURATION (OFF-PEAK ONLY)")
print(pivot_table.to_string())

# --- 4. SUMMARY STATS (MEAN/MEDIAN) ---
stats = off_peak_df.groupby('member_casual')['duration_min'].agg(['mean', 'median']).round(1)
stats.columns = ['Avg Duration (min)', 'Median Duration (min)']
print("\nSUMMARY STATS (OFF-PEAK)")
print(stats.to_string())