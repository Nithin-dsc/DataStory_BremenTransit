# Let's write a python script to generate 3 comprehensive visualizations:
# 1. EDA Distribution: Overall Delay Distribution (Histogram/KDE)
# 2. Main Question 1: Top 15 Bottleneck Stations (Bar chart with station names)
# 3. Main Question 2: Hourly Delay Trends (Line plot comparing mean vs median across hours)

import zipfile
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set professional plotting theme
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.sans-serif': 'Arial', 'font.size': 11})

# Load lookup table
lookup_path = Path("lookup_table.csv")
if not lookup_path.exists():
    lookup_path = Path("./update_data/lookup_table.csv")
df_lookup = pd.read_csv(lookup_path)

# Extract and combine a robust sample of telemetry files from zip to generate the charts
zip_path = Path("update_data (1).zip")
with zipfile.ZipFile(zip_path, 'r') as z:
    csv_names = [name for name in z.namelist() if name.endswith('.csv')][:500] # 500 files for solid EDA sample
    dfs = []
    for name in csv_names:
        with z.open(name) as f:
            dfs.append(pd.read_csv(f))
    telemetry_df = pd.concat(dfs, ignore_index=True)

# Clean telemetry
telemetry_df['parsed_timestamp'] = pd.to_datetime(telemetry_df['timestamp_fetched'], errors='coerce')
telemetry_df['delay_seconds'] = telemetry_df['delay_seconds'].fillna(0).astype(int)

# Merge with lookup table
merged_df = telemetry_df.merge(df_lookup[['stop_id', 'stop_name', 'route_short_name']], on='stop_id', how='left')

# --- CHART 1: EDA - Delay Distribution ---
plt.figure(figsize=(10, 5))
sns.histplot(merged_df[merged_df['delay_seconds'] <= 1800]['delay_seconds'], bins=50, color='#337ab7', kde=True)
plt.title("EDA: Distribution of Public Transport Delays (0 - 30 Minutes)", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Delay Duration (Seconds)", fontsize=12)
plt.ylabel("Frequency (Trip Observations)", fontsize=12)
plt.tight_layout()
eda_chart_path = "dashboard_chart_0_eda.png"
plt.savefig(eda_chart_path, dpi=300)
plt.close()

# --- CHART 2: Question 1 - Top Bottleneck Stations ---
hotspots = merged_df.groupby('stop_name')['delay_seconds'].mean().reset_index()
hotspots = hotspots.sort_values(by='delay_seconds', ascending=False).head(15)

plt.figure(figsize=(12, 6))
sns.barplot(data=hotspots, x='stop_name', y='delay_seconds', palette='Reds_r')
plt.title("Main Question 1: Top 15 Bottleneck Stations by Average Delay", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Station Name", fontsize=12)
plt.ylabel("Average Delay (Seconds)", fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
q1_chart_path = "dashboard_chart_1_bottlenecks.png"
plt.savefig(q1_chart_path, dpi=300)
plt.close()

# --- CHART 3: Question 2 - Hourly Delay Trends ---
merged_df['hour'] = merged_df['parsed_timestamp'].dt.hour
hourly = merged_df.groupby('hour')['delay_seconds'].agg(['mean', 'median']).reset_index()

plt.figure(figsize=(10, 5))
plt.plot(hourly['hour'], hourly['mean'], marker='o', color='#d9534f', linewidth=2.5, label='Mean Delay (s)')
plt.plot(hourly['hour'], hourly['median'], marker='s', color='#337ab7', linewidth=2, linestyle='--', label='Median Delay (s)')
plt.title("Main Question 2: Network Delay Patterns Across Hours of the Day", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Hour of Day (24-Hour Format)", fontsize=12)
plt.ylabel("Delay (Seconds)", fontsize=12)
plt.xticks(range(0, 24))
plt.legend(frameon=True)
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
q2_chart_path = "dashboard_chart_2_hourly.png"
plt.savefig(q2_chart_path, dpi=300)
plt.close()

print("All 3 dashboard charts generated successfully.")