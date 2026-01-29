
import pandas as pd
import pickle
from pathlib import Path

# --- Configuration ---
DATE = "2025-12-18"
PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "12-18"

print(f"--- Inspecting data for date: {DATE} ---")
print(f"Loading data from: {PROCESSED_DATA_DIR}\n")

# --- Load Artifacts ---
try:
    # Load leaf_values
    with open(PROCESSED_DATA_DIR / f"{DATE}_leaf_values.pkl", "rb") as fp:
        leaf_values = pickle.load(fp)

    # Load mapping_dict
    mapping_dict_df = pd.read_csv(PROCESSED_DATA_DIR / f"{DATE}_mapping_dict_df.csv", index_col=0)
    mapping_dict = pd.Series(mapping_dict_df.iloc[:, 0].values, index=mapping_dict_df.index).to_dict()

except FileNotFoundError as e:
    print(f"ERROR: Could not find data file. {e}")
    exit()

# --- Inspection Logic ---
print(f"Found {len(leaf_values)} leaf values.")
print("1. Checking the order of `leaf_values` from the pickle file...")
print("   - First 15 leaf values:", leaf_values[:15])
is_sorted_alpha = (leaf_values == sorted(leaf_values))
print(f"   - Is the list alphabetically sorted? -> {is_sorted_alpha}\n")

# Recreate the map from the validation script
# This map should translate a global index (from mapping_dict) to a local index (0 to N-1)
leaf_idx_to_leaf_map = {mapping_dict[cid]: i for i, cid in enumerate(leaf_values)}

print("2. Checking the `leaf_idx_to_leaf_map` created from this data...")
map_items = list(leaf_idx_to_leaf_map.items())
print("   - First 15 entries in the map: {Global Index: Local Index}")
for i, (k, v) in enumerate(map_items):
    if i >= 15:
        break
    print(f"     {{ {k}: {v} }}")

is_identity_map = all(k == v for k, v in leaf_idx_to_leaf_map.items())
print(f"\n   - Is the map an identity map (i.e., global_idx == local_idx for all leaves)? -> {is_identity_map}")

if not is_identity_map:
    print("\n   *** WARNING: Map is NOT an identity map. This indicates a potential issue. ***")
    print("      This means `mapping_dict` was not created from a sorted list of leaves,")
    print("      or `leaf_values.pkl` is not sorted.")
else:
    print("\n   - OK: The map is a perfect identity map for the leaf nodes.")

print("\n--- Inspection Complete ---")
