import pandas as pd
import os
import glob

folder = "./data"  # change to your folder
output_file = "0-combined_output.csv"

csv_files = glob.glob(os.path.join(folder, "*.csv"))

dfs = []
for file in csv_files:
    df = pd.read_csv(file)
    df["source_file"] = os.path.basename(file)
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)
combined.to_csv(output_file, index=False)

print(f"Saved combined CSV with {len(combined)} rows to {output_file}")
