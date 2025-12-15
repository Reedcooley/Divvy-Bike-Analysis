import pandas as pd

file_path = '0-processed_ride_data_with_speed.csv'
print(f"Validating file: {file_path}")
df = pd.read_csv(file_path)

print("\n--- VALIDATION REPORT ---")

# CHECK 1: Speed Logic (New)
# Define "Out of the Ordinary" as > 50km/h (Professional Cyclist / Car speeds)
speed_limit = 50 
super_speeders = df[df['speed_kmh'] > speed_limit]

print(f"1. Speed Check (> {speed_limit} km/h):")
if len(super_speeders) > 0:
    print(f"   ⚠️  WARNING: Found {len(super_speeders)} rides with suspicious speeds.")
    print("   Sample of high speed rides:")
    # showing time, distance and speed to see if it makes sense
    print(super_speeders[['ride_time', 'net_ride_distance_km', 'speed_kmh']].head(5))
else:
    print("   ✅ All speeds look normal (under 50 km/h).")

# CHECK 2: Commute Weekend Logic
weekend_commutes = df[(df['commut'] == True) & (df['Weekday'] == False)]
if len(weekend_commutes) == 0:
    print("\n2. Commute Logic: ✅ SUCCESS (No weekend commutes found).")
else:
    print(f"\n2. Commute Logic: ❌ FAILURE ({len(weekend_commutes)} weekend commutes found).")

# CHECK 3: Negative/Zero Durations causing infinite speed
# If ride_time is 0 but distance > 0, speed would be Inf (or NaN in our script)
# We check if we have any valid distance but 0 duration
magic_travel = df[(df['net_ride_distance_km'] > 0.1) & (df['ride_time'] == "0:00:00")]
if len(magic_travel) > 0:
    print(f"\n3. Data Logic: ⚠️ Found {len(magic_travel)} rows with Distance but 0 Duration.")
else:
    print("\n3. Data Logic: ✅ No instantaneous travel detected.")

print("\n--- End Report ---")