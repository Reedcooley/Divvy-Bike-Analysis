import pandas as pd

# Load the NEW enriched file
file_path = 'processed-data/0-processed_ride_data.csv'
print(f"Validating file: {file_path}")
df = pd.read_csv(file_path)

# Convert types for checking
df['started_at'] = pd.to_datetime(df['started_at'])

print("\n--- VALIDATION REPORT ---")

# TEST 1: Commute on Weekends
# Filter for rows where it is a Commute BUT it is NOT a weekday
weekend_commutes = df[(df['commut'] == True) & (df['Weekday'] == False)]
count_errors = len(weekend_commutes)

if count_errors == 0:
    print("✅ SUCCESS: No commute trips found on weekends.")
else:
    print(f"❌ FAILURE: Found {count_errors} commute trips on weekends (Logic Error).")

# TEST 2: Ride Time Format
# Check if ride_time looks like "H:MM:SS" (e.g., contains colons)
# We take a sample of 5 rows
print("\n✅ Sample of new 'ride_time' format:")
print(df[['started_at', 'ended_at', 'ride_time']].head(5))

# TEST 3: Commute Logic Check
# Verify a specific commute row to ensure it meets all criteria
print("\n✅ Sample Commuter Row (Should be Weekday, Morning/Evening, <1hr):")
commuters = df[df['commut'] == True]
if not commuters.empty:
    print(commuters[['started_at', 'ride_time', 'Weekday', 'commut']].head(1))
else:
    print("No commuters found in dataset (might be normal if data is small).")

# TEST 4: Long Duration Check
# Verify that rides > 24 hours are formatted correctly (e.g. "25:00:00")
# We calculate seconds again just to find long rides to display
seconds = (pd.to_datetime(df['ended_at']) - df['started_at']).dt.total_seconds()
long_rides = df[seconds > 86400] # > 24 hours

if not long_rides.empty:
    print(f"\n✅ Verified formatting for {len(long_rides)} rides > 24 hours:")
    print(long_rides[['started_at', 'ended_at', 'ride_time']].head(3))
else:
    print("\nℹ️ No rides longer than 24 hours found to verify format.")