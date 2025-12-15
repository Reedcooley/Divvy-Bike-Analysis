# Divvy Bike-Share Analysis

![Main Insight Chart](visualizations_simplified/pie_charts.png)

## Project Overview
This project analyzes Divvy bike-share data to identify behavioral differences between casual riders and annual members, revealing that:
1. Over **22%** of casual riders exhibit commuter-like patterns.
2. Casual riders demonstrate significant potential for **short utility trips** (micro-mobility).

The findings support actionable marketing strategies to convert these "stealth commuters" and micro-mobility users into annual subscribers.

## Project Steps

### PREPARE
* Downloaded CSVs from [Divvy Data S3 Bucket](https://divvy-tripdata.s3.amazonaws.com/index.html).
* Took 12 monthly CSVs from 12/2024 to 11/2025.
* Used `merge-data.py` script to combine into one CSV with an added column for document source.

### PROCESS

#### Data Enrichment & Feature Engineering
* Calculated `ride_time` (duration) by subtracting `started_at` from `ended_at`.
* Formatted `ride_time` as `H:MM:SS` (rounding to the nearest second) for compatibility with visualization tools.
* Extracted `start_time`, `end_time`, and `Weekday` (Boolean) from timestamps.
* Calculated `net_ride_distance_km` using the Haversine formula to measure the "as-the-crow-flies" distance between start and end coordinates.
* Calculated `speed_kmh` (Distance / Time) to identify impossible travel speeds.

#### Commuter Logic Definition
Created a `commut` boolean flag to segment likely commuter trips based on the following strict criteria:
* **Time:** Trip started between 06:00–10:00 (Morning Rush) OR 17:00–20:00 (Evening Rush).
* **Day:** Trip occurred on a Weekday (Mon–Fri).
* **Duration:** Trip lasted less than 60 minutes.
* **Distance:** Trip distance was > 0 km (excluding round trips that return to the same station).

#### Data Cleaning & Quality Control
* **Removed Negative Durations:** Filtered out rows where `ended_at` occurred before `started_at`.
* **Removed "Magic Travel" Errors:** Filtered out rows with valid distance (> 0 km) but zero duration (`0:00:00`).
* **Removed GPS Drift/Speed Outliers:** Filtered out rides with a calculated speed > 32 km/h (approx. 20 mph).
    * *Rationale:* 99% of riders traveled slower than 26.2 km/h. The 32 km/h threshold accounts for the mechanical speed cap of Divvy e-bikes while removing severe GPS errors.

#### Metadata & Integrity Checks
* **Filtered "Test" Stations:** Scanned `start_station_name` for administrative keywords (e.g., "TEST", "REPAIR", "WATSON") to remove maintenance trips.
* **Standardized Bike Types:** Harmonized legacy terminology (`docked_bike`) with current naming conventions (`classic_bike`).
* **Validated Geographic Bounds:** Screened coordinates to flag outliers falling significantly outside the city's operating zone.
* **Checked Uniqueness:** Verified `ride_id` was a unique primary key.

### ANALYZE
* **Segmented User Profiles (Member vs. Casual):**
* **Identified "Stealth Commuters":** Calculated that **22.4%** of Casual rides fit the strict "Commuter" profile (Weekday, Rush Hour, <1 hr), revealing a high-value segment of users who are already paying per-ride prices for daily utility usage.
* **Contrasted Weekend Behavior:** Conducted a deep dive into Saturday/Sunday usage. Found that Casual riders are **2.5x more likely** to take Round Trips (11.5% vs 4.7%) and maintain an average duration nearly double that of members (25.8 min vs 13.6 min), confirming distinct "Leisure/Sightseeing" intent.
* **Validated "Micro-Mobility" Usage:** Analyzed ride durations during off-peak hours to test utility usage outside of work commutes. Discovered that **57.7%** of Member rides are under 10 minutes (compared to 41.7% for Casuals), proving Members treat the bike as a "pedestrian accelerator" for quick errands.
* **Assessed Long-Ride Risk:** Noted that **18.9%** of Casual weekend rides last longer than 30 minutes (vs 7.1% for Members). This highlights a specific pain point for Casual users (accumulating per-minute costs).

### SHARE
* **Created side-by-side donut charts to visualize ride type by user segment:**
    * Categorized all rides into four distinct behaviors:
        * **Commute:** (Mon-Fri, Rush Hour, <1hr).
        * **Short Snap:** (Off-peak utility trips <10 mins).
        * **Weekend Joy Ride:** (Sat/Sun leisure trips >30 mins).
        * **Other:** General usage.
    * *Insight:* The combined "Utility" segments (Commute + Short Snap) make up a substantial, convertible portion of Casual ridership.

* **Generated a "Utility Curve" analyzing ride duration during off-peak hours:**
    * **Key Insights:**
        * Commutes and Short Snaps are common for both user types, with higher portions for Members (>70% of rides).
        * The **22.4%** of casual riders that appear to be using bikes for commuting represent a "stealth commuter" group ripe for conversion.
        * The biggest disparity is in off-peak rides **under 10 minutes** (especially under 5 minutes). Members use the service as a "pedestrian accelerator" for short utility trips in over 50% of off-peak rides.
        * Over 40% of casual riders also use it this way, but they are paying a per-minute premium and unlock fees to do so.

### ACT (Recommendations)

**1. Target "Stealth Commuters" with Digital Pushes**
* **Strategy:** Trigger in-app notifications or emails to casual riders immediately after they complete a weekday ride between 6–10 AM or 5–8 PM.
* **Message:** *"That ride cost you $X. With an Annual Membership, it would have been included. Upgrade today."*

**2. Market "Micro-Trip" Convenience**
* **Strategy:** Highlight the 0–10 minute "Short Snap" utility in ads to show non-members a use case they haven't considered (e.g., getting to the bus stop or grocery store).
* **Message:** *"Too far to walk, too short to drive? Unlock a bike for $0 with membership."*