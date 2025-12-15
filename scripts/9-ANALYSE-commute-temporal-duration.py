import pandas as pd

# Load the CLEANED final file
file_path = 'processed-data/0-processed_ride_data_with_speed_cleaned.csv'
print(f"Loading {file_path}...")
df = pd.read_csv(file_path)

print("\n--- ANALYSIS: MEMBER vs CASUAL ---")

# 1. Total Counts
total_rides = len(df)
grouped = df.groupby('member_casual')

# 2. The "Commuter" Insight
# We calculate the mean of the boolean (True=1, False=0) to get the %
commuter_stats = grouped['commut'].agg(['count', 'sum', 'mean']).reset_index()
commuter_stats.columns = ['User Type', 'Total Rides', 'Commute Trips', 'Commuter %']
commuter_stats['Commuter %'] = (commuter_stats['Commuter %'] * 100).round(2)

print("\n1. Who is commuting?")
print(commuter_stats.to_string(index=False))

# 3. Temporal Habits (Weekend vs Weekday)
# We calculate % of rides that happen on a Weekday
weekday_stats = grouped['Weekday'].mean().reset_index()
weekday_stats.columns = ['User Type', 'Weekday %']
weekday_stats['Weekday %'] = (weekday_stats['Weekday %'] * 100).round(2)
weekday_stats['Weekend %'] = 100 - weekday_stats['Weekday %']

print("\n2. When do they ride?")
print(weekday_stats.to_string(index=False))

# 4. Ride Behavior (Duration & Distance)
# We use numeric conversion for ride_time just for averaging
df['duration_min'] = (pd.to_datetime(df['ended_at']) - pd.to_datetime(df['started_at'])).dt.total_seconds() / 60

behavior_stats = grouped[['duration_min', 'net_ride_distance_km', 'speed_kmh']].mean().round(2).reset_index()
behavior_stats.columns = ['User Type', 'Avg Duration (min)', 'Avg Distance (km)', 'Avg Speed (km/h)']

print("\n3. How do they ride?")
print(behavior_stats.to_string(index=False))

# 5. Bike Preference
# See if casuals prefer electric bikes more than members
bike_pref = df.groupby(['member_casual', 'rideable_type']).size().unstack(fill_value=0)
# Calculate percentage share for each user type
bike_pref_pct = bike_pref.div(bike_pref.sum(axis=1), axis=0) * 100
print("\n4. Bike Preference (% of their own rides):")
print(bike_pref_pct.round(1))