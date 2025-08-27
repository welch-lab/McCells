import cellxgene_census
import tiledbsoma as soma
import pandas as pd
import numpy as np
import os
import pickle # For loading cell_type_list

def download_and_filter_data():
    # Define paths for input files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mart_export_path = os.path.join(script_dir, 'mart_export.txt')
    

    # Load gene list (protein-coding only)
    biomart = pd.read_csv(mart_export_path)
    coding_only = biomart[biomart['Gene type'] == 'protein_coding']
    gene_list = coding_only['Gene stable ID'].to_list()
    var_val_filter = '''feature_id in {}'''.format(gene_list)

    # Define organism and initial column names
    organism = "Homo sapiens"
    col_names = {"obs": ["cell_type_ontology_term_id", "assay", "is_primary_data"]} # Need these for filtering

    # Open the Census (once)
    with cellxgene_census.open_soma(census_version="stable") as census:
        experiment = census["census_data"]["homo_sapiens"]

        # Read all obs metadata to filter cell types
        print("Reading filtered human cell metadata to identify valid cell types...")
        obs_initial_filter = '''assay == "10x 3' v3" and is_primary_data == True'''
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
        batch_size = 80 # Example batch size, adjust as needed
        cell_type_batches = [intersection_cell_types[i:i + batch_size] for i in range(0, cell_n, batch_size)]

        print(f"Divided into {len(cell_type_batches)} batches.")

        # Loop through batches and download data
        for i, batch_cell_types in enumerate(cell_type_batches):
            print(f"Processing batch {i+1}/{len(cell_type_batches)}...")
            obs_val_filter = '''assay == "10x 3' v3" and is_primary_data == True and cell_type_ontology_term_id in {}'''.format(batch_cell_types)

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

if __name__ == "__main__":
    download_and_filter_data()