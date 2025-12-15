import pandas as pd
import numpy as np

# Load the file
df = pd.read_csv('0-' \
'processed-data/0-processed_ride_data_with_speed.csv')

# Ensure we have speed
# (If you are running this on the raw file, copy the speed calc logic here)
print("--- SPEED DISTRIBUTION ---")
print(df['speed_kmh'].describe(percentiles=[.5, .75, .90, .95, .99, .999]))

# Show the 'Cliff'
print("\n--- The Top 1% of Speeds ---")
top_1_percent = df[df['speed_kmh'] > df['speed_kmh'].quantile(0.99)]
print(top_1_percent[['ride_time', 'net_ride_distance_km', 'speed_kmh']].sort_values('speed_kmh').head(10))