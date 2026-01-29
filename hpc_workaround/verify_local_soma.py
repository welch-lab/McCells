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


        # --- 4. Verify data is not deprecated by loading a batch ---
        print("--- Verifying data is not deprecated by loading a batch ---")
        from tiledbsoma_ml import ExperimentDataset, experiment_dataloader
        import numpy as np

        with census.axis_query(
            measurement_name="RNA",
            obs_query=soma.AxisQuery(value_filter='assay == "10x 3\' v3" and is_primary_data == True'),
        ) as query:
            ds = ExperimentDataset(query, obs_column_names=["cell_type_ontology_term_id"],
                                   layer_name="raw", batch_size=256, shuffle=False)
            dl = experiment_dataloader(ds)

            for X, obs in dl:
                print(f"Shape: {X.shape}")
                print(f"Mean: {X.mean():.4f}")
                print(f"Std: {X.std():.4f}")
                print(f"Nonzero: {(X != 0).sum()}/{X.size} ({(X != 0).mean()*100:.1f}%)")
                print(f"Min: {X.min():.4f}, Max: {X.max():.4f}")
                break
        print("\n" + "-" * 80 + "\n")

        print("--- Sanity check successful! The SOMA database appears to be functioning correctly. ---")

except Exception as e:
    print(f"An error occurred: {e}")
    print("--- Sanity check failed. There might be an issue with your SOMA database. ---")