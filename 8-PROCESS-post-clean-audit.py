import pandas as pd

# Load your cleaned file
df = pd.read_csv('0-processed_ride_data_with_speed_cleaned.csv')

print("--- FINAL AUDIT ---")

# CHECK 1: Test Stations
# Look for 'TEST', 'REPAIR', 'BASE' in station names (case insensitive)
# We fillna('') so we don't error out on missing station names
test_stations = df[df['start_station_name'].fillna('').str.upper().str.contains('TEST|REPAIR|WATSON')]
print(f"1. Test/Repair Stations found: {len(test_stations)}")
if len(test_stations) > 0:
    print(test_stations['start_station_name'].unique())

# CHECK 2: Rideable Type Consistency
print("\n2. Rideable Types present:")
print(df['rideable_type'].value_counts())
# Tip: If you see 'docked_bike', consider merging it into 'classic_bike'

# CHECK 3: Duplicate Ride IDs
# ride_id should be a primary key (unique)
duplicates = df[df.duplicated(subset=['ride_id'])]
print(f"\n3. Duplicate Ride IDs: {len(duplicates)}")

# CHECK 4: Geographic Outliers (Chicago is roughly Lat 41-42, Long -87)
# Checks for 0,0 coordinates or points way outside the city
outliers = df[(df['start_lat'] < 41) | (df['start_lat'] > 43) | 
              (df['start_lng'] > -87) | (df['start_lng'] < -88)]
print(f"\n4. GPS Outliers (Outside Chicago approx area): {len(outliers)}")

print("\n--- Audit Complete ---")