import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# --- CONFIGURATION ---
input_file = 'processed-data/0-processed_ride_data_with_speed_cleaned.csv'
output_dir = 'visualizations'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print(f"Loading {input_file}...")
df = pd.read_csv(input_file)

# Convert timestamps
df['started_at'] = pd.to_datetime(df['started_at'])
df['ended_at'] = pd.to_datetime(df['ended_at'])

# --- CATEGORIZATION LOGIC ---
print("Categorizing Rides...")

# 1. Define Helper Columns
df['duration_min'] = (df['ended_at'] - df['started_at']).dt.total_seconds() / 60
df['Weekday'] = df['started_at'].dt.dayofweek < 5 # True=Mon-Fri
hour = df['started_at'].dt.hour
is_rush_hour = (hour >= 6) & (hour < 10) | (hour >= 17) & (hour < 20)
df['is_commute_time'] = df['Weekday'] & is_rush_hour

# 2. Define Categories (Priority Based)
def categorize_ride(row):
    # Category 1: Commute (Already rigorously defined in 'commut' column)
    if row['commut']:
        return 'Commute'
    
    # Category 2: Weekend Joy Ride (Weekend + >30 mins)
    if (not row['Weekday']) and (row['duration_min'] > 30):
        return 'Weekend Joy Ride'
    
    # Category 3: Short Snap (Outside Commute Time + <10 mins)
    # Note: 'Outside Commute Time' includes all Weekends and Off-Peak Weekdays
    if (not row['is_commute_time']) and (row['duration_min'] < 10):
        return 'Short Snap (<10m)'
    
    # Category 4: Other
    return 'Other'

# Apply categorization (this might take a few seconds on large data)
# Optimization: Vectorized approach is faster than .apply
conditions = [
    (df['commut'] == True),
    (df['Weekday'] == False) & (df['duration_min'] > 30),
    (df['is_commute_time'] == False) & (df['duration_min'] < 10)
]
choices = ['Commute', 'Weekend Joy Ride', 'Short Snap (<10m)']
df['ride_category'] = np.select(conditions, choices, default='Other')

# =============================================================================
# CHART 1: PIE CHARTS (Member vs Casual)
# =============================================================================
print("Generating Pie Charts...")

# Group by User Type and Category
pie_data = df.groupby(['member_casual', 'ride_category']).size().unstack(fill_value=0)

# Colors
colors = {
    'Commute': '#2ecc71',           # Green (Money/Go)
    'Short Snap (<10m)': '#3498db', # Blue (Quick/Utility)
    'Weekend Joy Ride': '#e67e22',  # Orange (Leisure/Fun)
    'Other': '#bdc3c7'              # Grey
}
category_order = ['Commute', 'Short Snap (<10m)', 'Weekend Joy Ride', 'Other']
color_list = [colors[cat] for cat in category_order]

fig, axes = plt.subplots(1, 2, figsize=(14, 7))
fig.suptitle('Trip Type Segmentation: How They Use the Bikes', fontsize=16, fontweight='bold')

# Function to make the pie chart
def make_pie(ax, user_type, title):
    data = pie_data.loc[user_type].reindex(category_order)
    wedges, texts, autotexts = ax.pie(
        data, 
        labels=data.index, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=color_list,
        pctdistance=0.85,
        explode=[0.05, 0.05, 0.05, 0] # Explode the key segments slightly
    )
    
    # Styling text
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        
    # Draw circle for Donut chart look (optional, but looks cleaner)
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    ax.add_artist(centre_circle)
    
    ax.set_title(title, fontsize=14, fontweight='bold', color='#2c3e50')

# Plot Member
make_pie(axes[0], 'member', 'MEMBERS\n(Efficient & Routine)')

# Plot Casual
make_pie(axes[1], 'casual', 'CASUALS\n(Leisure & Potential)')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(f"{output_dir}/pie_charts.png", dpi=300)
plt.close()


# =============================================================================
# CHART 2: THE UTILITY CURVE
# =============================================================================
print("Generating Utility Curve...")

# Filter for Off-Peak only
off_peak_df = df[~df['is_commute_time']].copy()

# Bins
bins = [0, 5, 10, 20, 30, 60]
labels = ['0-5', '5-10', '10-20', '20-30', '30-60']
off_peak_df['duration_bin'] = pd.cut(off_peak_df['duration_min'], bins=bins, labels=labels)

# Calculate %
dist_data = off_peak_df.groupby(['member_casual', 'duration_bin'], observed=False).size().reset_index(name='count')
totals = off_peak_df.groupby('member_casual').size().reset_index(name='total')
dist_data = dist_data.merge(totals, on='member_casual')
dist_data['pct'] = (dist_data['count'] / dist_data['total'] * 100)
pivot = dist_data.pivot(index='duration_bin', columns='member_casual', values='pct')

# Plot
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(labels))
width = 0.35

ax.bar(x - width/2, pivot['member'], width, label='Member', color='#2980b9')
ax.bar(x + width/2, pivot['casual'], width, label='Casual', color='#95a5a6')

ax.set_title('Ride Duration Distribution (Off-Peak Hours Only)', fontsize=14, fontweight='bold')
ax.set_xlabel('Ride Duration (Minutes)')
ax.set_ylabel('Percentage of Rides')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

plt.savefig(f"{output_dir}/utility_curve.png", dpi=300)
plt.close()

print(f"--- DONE ---")
print(f"Pie Charts saved to: {output_dir}/simplified_pie_charts.png")
print(f"Utility Curve saved to: {output_dir}/utility_curve.png")