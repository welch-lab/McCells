#!/usr/bin/env python

import cellxgene_census
import tiledbsoma
import anndata as ad
import os

# --- Configuration ---

# Path to your large, locally downloaded SOMA database
source_soma_path = "/scratch/sigbio_project_root/sigbio_project25/jingqiao/mccell-single/soma_db_homo_sapiens"

# Path where the new, smaller, filtered SOMA database will be created
filtered_soma_path = "/scratch/sigbio_project_root/sigbio_project25/jingqiao/mccell-single/soma_db_homo_sapiens_filtered"

# The filter to apply
# This is the same filter from your get_h5ad_links.py script
value_filter = 'assay == "10x 3\' v3" and is_primary_data == True'

# --- Script ---

print(f"Opening source SOMA database at: {source_soma_path}")
with cellxgene_census.open_soma(uri=source_soma_path) as census:

    print(f"Querying data with filter: '{value_filter}'")
    query = census.axis_query(
        measurement_name="RNA",
        obs_query=tiledbsoma.AxisQuery(value_filter=value_filter)
    )

    # --- This is the memory-intensive step ---
    # It loads the entire filtered dataset into memory before it can be written back to disk.
    # Ensure you are running this on a machine with enough RAM to hold the filtered data.
    print("Loading filtered data into memory (this may take a while and use a lot of RAM)...")
    filtered_adata = query.to_anndata(X_name="raw")

    print("\nFiltered data summary:")
    print(filtered_adata)

    os.makedirs(filtered_soma_path, exist_ok=True)

    print(f"\nWriting filtered data to new SOMA database at: {filtered_soma_path}")
    tiledbsoma.io.from_anndata(
        experiment_uri=filtered_soma_path,
        anndata=filtered_adata,
        measurement_name="RNA"
    )

    print("\nProcess complete.")
    print(f"A smaller, filtered SOMA database has been created at: {filtered_soma_path}")
