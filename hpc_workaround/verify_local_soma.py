#!/usr/bin/env python

import tiledbsoma as soma
import pandas as pd

# --- Configuration ---

# Set pandas display options for better readability in the terminal
pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 140)

# Path to your local SOMA database
local_soma_path = "/scratch/sigbio_project_root/sigbio_project25/jingqiao/mccell-single/soma_db_homo_sapiens"

# --- Verification Script ---

print(f"--- Opening SOMA database at: {local_soma_path} ---\\n")

try:
    with soma.Experiment.open(local_soma_path) as census:

        # --- 1. Read the first 5 records from the 'obs' (cell metadata) dataframe ---
        print("--- First 5 Cells (obs) ---")
        obs_head = census.obs.read(limit=5).concat().to_pandas()
        print(obs_head)
        print("\\n" + "-" * 80 + "\\n")

        # --- 2. Read the first 5 records from the 'var' (gene metadata) dataframe ---
        print("--- First 5 Genes (var) ---")
        var_head = census.ms['RNA'].var.read(limit=5).concat().to_pandas()
        print(var_head)
        print("\\n" + "-" * 80 + "\\n")

        # --- 3. Read a small slice of the 'X' matrix ---
        # Let's read the data for the first 5 cells and first 10 genes
        print("--- Data slice from X['raw'] matrix (5 cells x 10 genes) ---")
        query = census.axis_query(
            measurement_name="RNA",
            coords=(slice(5), slice(10))  # Slice for obs (cells) and var (genes)
        )

        # .tables() returns an iterator, we'll just get the first chunk
        x_chunk = next(query.X('RNA')['raw'].tables())

        # Convert to pandas for display. The result is a sparse matrix format.
        x_df = x_chunk.to_pandas()
        print(x_df)
        print("\\n" + "-" * 80 + "\\n")

       

except Exception as e:
    print(f"An error occurred: {e}")
    print("--- Sanity check failed. There might be an issue with your SOMA database. ---")
