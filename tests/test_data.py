import sys
import os

# Add parent directory to path to allow importing utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_loader import load_data
import pandas as pd

data = load_data()
impact_dat_all = data["impact_dat_all"]
readiness_cat_all = data["readiness_cat_all"]

print("--- Impact Data (Overall) ---")
overall_impact = impact_dat_all[impact_dat_all["country"] == "Overall"]
print(overall_impact)
print(f"Shape: {overall_impact.shape}")
print("Duplicates:", overall_impact.duplicated(subset=['category']).any())

print("\n--- Readiness Data (Overall) ---")
overall_readiness = readiness_cat_all[readiness_cat_all["country"] == "Overall"]
print(overall_readiness)
print(f"Shape: {overall_readiness.shape}")
print("Duplicates:", overall_readiness.duplicated(subset=['category']).any())