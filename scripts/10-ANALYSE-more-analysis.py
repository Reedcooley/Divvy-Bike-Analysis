import pandas as pd

# Load the CLEANED file
file_path = 'processed-data/0-processed_ride_data_with_speed_cleaned.csv'
print(f"Loading {file_path}...")
df = pd.read_csv(file_path)

# --- THE FIX: Convert text columns back to datetime objects ---
df['started_at'] = pd.to_datetime(df['started_at'])
df['ended_at'] = pd.to_datetime(df['ended_at'])

# 1. Filter for Weekends ONLY
print("\n--- WEEKEND DEEP DIVE (Saturday & Sunday) ---")
# Saturday=5, Sunday=6. If you have a Boolean 'Weekday', False means Weekend.
weekend_df = df[df['Weekday'] == False].copy()
print(f"Total Weekend Rides: {len(weekend_df)}")

# 2. Group by Member vs Casual
grouped = weekend_df.groupby('member_casual')

# 3. Calculate "Leisure Indicators"
# Calculate duration in minutes
weekend_df['duration_min'] = (weekend_df['ended_at'] - weekend_df['started_at']).dt.total_seconds() / 60

# Indicator A: Duration Stats (Mean vs Median)
duration_stats = grouped['duration_min'].agg(['mean', 'median']).round(1)
duration_stats.columns = ['Avg Duration (min)', 'Median Duration (min)']

# Indicator B: Peak Start Hour (When do they start?)
# We find the hour with the highest count for each group
peak_hours = weekend_df.groupby(['member_casual', weekend_df['started_at'].dt.hour])['ride_id'].count()

# FIX: peak_hours['casual'] is already just the hours, so idxmax() returns the hour directly
peak_casual = peak_hours['casual'].idxmax() 
peak_member = peak_hours['member'].idxmax()

# Indicator C: Round Trip % (Start Station == End Station)
# Using distance < 0.05km as a proxy for returning to the same spot
# (This includes people who undock and redock immediately, but also legitimate round trips)
round_trip_counts = weekend_df[weekend_df['net_ride_distance_km'] < 0.05].groupby('member_casual').size()
total_counts = grouped.size()
round_trip_pct = (round_trip_counts / total_counts * 100).round(2)

# Combine into a summary dataframe
summary = duration_stats.copy()
summary['Peak Start Hour'] = [f"{peak_casual}:00", f"{peak_member}:00"]
summary['Round Trip %'] = round_trip_pct

print(summary.to_string())

# 4. Long Ride Analysis (> 30 mins)
print("\n--- Long Ride Analysis (> 30 mins) ---")
long_rides = weekend_df[weekend_df['duration_min'] > 30]
long_ride_share = (long_rides.groupby('member_casual').size() / total_counts * 100).round(1)
print("Percentage of Weekend rides that last > 30 minutes:")
print(long_ride_share)