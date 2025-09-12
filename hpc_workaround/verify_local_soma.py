#!/usr/bin/env python

import tiledbsoma as soma
import pandas as pd

# --- Configuration ---

# Set pandas display options for better readability in the terminal
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 160)

# Path to your local SOMA database
local_soma_path = "/scratch/sigbio_project_root/sigbio_project25/jingqiao/mccell-single/soma_db_homo_sapiens"

# --- Verification Script ---

print(f"--- Opening SOMA database at: {local_soma_path} ---\n")

try:
    with soma.Experiment.open(local_soma_path) as census:

        # --- 1. Read the first 5 records from the 'obs' (cell metadata) dataframe ---
        print("--- First 5 Cells (obs) ---")
        # CORRECTED: Use coords=(slice(5),) to read the first 5 rows
        obs_head = census.obs.read(coords=(slice(5),)).concat().to_pandas()
        print(obs_head)
        print("\n" + "-" * 80 + "\n")

        # --- 2. Read the first 5 records from the 'var' (gene metadata) dataframe ---
        print("--- First 5 Genes (var) ---")
        # CORRECTED: Use coords=(slice(5),) to read the first 5 rows
        var_head = census.ms['RNA'].var.read(coords=(slice(5),)).concat().to_pandas()
        print(var_head)
        print("\n" + "-" * 80 + "\n")

        # --- 3. Read a small slice of the 'X' matrix ---
        print("--- Data slice from X['raw'] matrix (5 cells x 10 genes) ---")
        query = census.axis_query(
            measurement_name="RNA",
            coords=(slice(5), slice(10))  # This was already correct
        )
        x_chunk = next(query.X('RNA')['raw'].tables())
        x_df = x_chunk.to_pandas()
        print(x_df)
        print("\n" + "-" * 80 + "\n")

        print("--- Sanity check successful! The SOMA database appears to be functioning correctly. ---")

except Exception as e:
    print(f"An error occurred: {e}")
    print("--- Sanity check failed. There might be an issue with your SOMA database. ---")