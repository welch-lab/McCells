#!/usr/bin/env python

import tiledbsoma as soma
import pandas as pd

# --- Configuration ---
# Set pandas display options for better readability in the terminal
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 160)

# Path to your local SOMA database
local_soma_path = "/scratch/sigbio_project_root/sigbio_project25/jingqiao/mccell-single/soma_db_homo_sapiens"

# --- Exploration Script ---

print(f"--- Exploring the schema of SOMA database at: {local_soma_path} ---\\n")

try:
    with soma.Experiment.open(local_soma_path) as census:

        # --- 1. Cell Metadata (`obs`) ---
        print("--- Cell Metadata (`obs`) ---")
        print("The `obs` dataframe contains metadata for each cell. Each row is a cell, each column is an attribute.")

        # Get and print all column names
        obs_columns = census.obs.keys()
        print(f"\nAvailable `obs` columns ({len(obs_columns)} total): {obs_columns}")

        # Read and print the first 5 rows with a selection of important columns
        print("\nExample data from the first 5 cells:")
        # We select a subset of columns to make the output readable
        obs_preview_columns = ['soma_joinid', 'dataset_id', 'assay', 'cell_type', 'tissue', 'disease', 'sex']
        obs_head = census.obs.read(limit=5, column_names=obs_preview_columns).concat().to_pandas()
        print(obs_head)
        print("\n" + "=" * 80 + "\n")

        # --- 2. Gene Metadata (`var`) ---
        print("--- Gene Metadata (`var`) ---")
        print("The `var` dataframe contains metadata for each gene (feature). Each row is a gene.")

        # Get and print all column names
        var_columns = census.ms['RNA'].var.keys()
        print(f"\nAvailable `var` columns ({len(var_columns)} total): {var_columns}")

        # Read and print the first 5 rows
        print("\nExample data from the first 5 genes:")
        var_head = census.ms['RNA'].var.read(limit=5).concat().to_pandas()
        print(var_head)
        print("\n" + "=" * 80 + "\n")

        # --- 3. Expression Data (`X['raw']`) ---
        print("--- Expression Data (`X['raw']`) ---")
        print("The `X` matrix contains the actual expression counts. It's a very large sparse matrix where:")
        print("- Rows correspond to cells (indexed by `soma_joinid` from the `obs` table).")
        print("- Columns correspond to genes (indexed by `soma_joinid` from the `var` table).")

        print("\nHere is a small 5x10 slice showing the raw counts for the first 5 cells and 10 genes:")
        query = census.axis_query(measurement_name="RNA", coords=(slice(5), slice(10)))
        x_chunk = next(query.X('RNA')['raw'].tables())
        x_df = x_chunk.to_pandas()
        print(x_df)

except Exception as e:
    print(f"An error occurred: {e}")
