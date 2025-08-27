#!/usr/bin/env python
import cellxgene_census
import tiledbsoma as soma
import pandas as pd
import numpy as np
import os
import pickle # For loading cell_type_list

def download_and_filter_data():
    """Downloads and filters data from the CellXGene Census.

    This script downloads data from the CellXGene Census, filters it based on a
    predefined list of protein-coding genes and cell types, and saves the
    filtered data in batches.

    The script is designed to be run on a high-performance computing (HPC)
    cluster, and it includes a progress tracking mechanism that allows it to be
    resumed if it is interrupted.
    """
    # Define paths for input files
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Path to the file with the list of genes
    mart_export_path = os.path.join(script_dir, 'mart_export.txt')
    

    # Load gene list (protein-coding only)
    # Read the list of genes from the file
    biomart = pd.read_csv(mart_export_path)
    # Filter for protein-coding genes
    coding_only = biomart[biomart['Gene type'] == 'protein_coding']
    # Get the list of gene IDs
    gene_list = coding_only['Gene stable ID'].to_list()
    # Create a filter for the query
    var_val_filter = f'''feature_id in {gene_list}'''

    # Define organism and initial column names
    organism = "Homo sapiens"
    # Define the columns to retrieve from the obs table
    col_names = {"obs": ["cell_type_ontology_term_id", "assay", "is_primary_data"]} # Need these for filtering

    # Open the Census (once)
    with cellxgene_census.open_soma(census_version="stable") as census:
        experiment = census["census_data"]["homo_sapiens"]

        # Read all obs metadata to filter cell types
        print("Reading filtered human cell metadata to identify valid cell types...")
        obs_initial_filter = f'''assay == "10x 3' v3" and is_primary_data == True'''
        exp_pd = experiment.obs.read(value_filter=obs_initial_filter, column_names=["cell_type_ontology_term_id"]).concat().to_pandas()
        cell_type_counts = exp_pd["cell_type_ontology_term_id"].value_counts()

        # Apply cell count threshold (5000)
        min_thresh = 5000
        good_mask = cell_type_counts > min_thresh
        valid_cell_types = cell_type_counts[good_mask].keys().to_list()

        # Intersect with predefined cell type list
        intersection_cell_types = list(set(valid_cell_types))
        print(f"Found {len(intersection_cell_types)} cell types matching criteria.")

        # Divide cell types into batches
        cell_n = len(intersection_cell_types)
        # This is a simplified batching, you might want to adjust the batch size
        # based on memory constraints and the number of cell types.
        batch_size = 1
        cell_type_batches = [intersection_cell_types[i:i + batch_size] for i in range(0, cell_n, batch_size)]

        print(f"Divided into {len(cell_type_batches)} batches.")

        # --- Batch processing with progress tracking ---
        progress_file = os.path.join(script_dir, 'download_progress.txt')
        start_batch = 0
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                content = f.read().strip()
                if content:
                    try:
                        start_batch = int(content)
                        print(f"Resuming from batch {start_batch + 1}...")
                    except ValueError:
                        print("Invalid content in progress file, starting from scratch.")
                else:
                    print("Progress file is empty, starting from scratch.")

        # Loop through batches and download data
        for i in range(start_batch, len(cell_type_batches)):
            batch_cell_types = cell_type_batches[i]
            print(f"Processing batch {i+1}/{len(cell_type_batches)}...")
            obs_val_filter = f'''assay == "10x 3' v3" and is_primary_data == True and cell_type_ontology_term_id in {batch_cell_types}'''

            query = soma.ExperimentAxisQuery(
                experiment=experiment,
                measurement_name="RNA",
                obs_query=soma.AxisQuery(
                    value_filter=obs_val_filter
                ),
                var_query=soma.AxisQuery(
                    value_filter=var_val_filter,
                ),
            )

            # Use to_anndata to get the AnnData object for this batch
            experiment_ad = query.to_anndata(X_name="raw", column_names=soma.AxisColumnNames(obs=["cell_type_ontology_term_id", "assay", "is_primary_data"]))

            # Save the AnnData object for this batch
            output_dir_data = "/nfs/turbo/umms-welchjd/Mccells-data"
            os.makedirs(output_dir_data, exist_ok=True) # Ensure directory exists
            output_filename = os.path.join(output_dir_data, f"filtered_data_batch_{i+1}.h5ad")
            experiment_ad.write(filename=output_filename, compression='gzip')
            print(f"Saved batch {i+1} to {output_filename} with shape {experiment_ad.shape}")

            # Update progress
            with open(progress_file, 'w') as f:
                f.write(str(i + 1))
            print(f"Progress saved. Last completed batch: {i+1}")

if __name__ == "__main__":
    download_and_filter_data()
