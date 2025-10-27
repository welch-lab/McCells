import pandas as pd
import torch
import pickle
from datetime import datetime
from src.utils.ontology_utils import load_ontology
from src.data_pipeline.data_loader import load_filtered_cell_metadata
from src.data_pipeline.preprocess_ontology import preprocess_data_ontology
from src.utils.paths import PROJECT_ROOT

def main():
    """
    Main function to run the full data preprocessing pipeline.
    """
    print("Starting data preprocessing pipeline...")

    # 1. Load the cached ontology object
    cl = load_ontology()
    if cl is None:
        return

    # Define the root of the ontology subgraph to be processed
    root_cl_id = 'CL:0000988'  # hematopoietic cell

    # 2. Load filtered cell metadata from CellXGene Census
    cell_obs_metadata = load_filtered_cell_metadata(cl, root_cl_id=root_cl_id)

    if cell_obs_metadata.empty:
        print("No cell metadata loaded. Aborting pipeline.")
        return

    # 3. Preprocess the ontology and cell data
    target_column = 'cell_type_ontology_term_id'

    print("Starting ontology preprocessing...")
    mapping_dict, leaf_values, internal_values, \
        marginalization_df, parent_child_df, exclusion_df = preprocess_data_ontology(
            cl, cell_obs_metadata, target_column,
            upper_limit=root_cl_id,
            cl_only=True, include_leafs=False
        )

    print(f"Preprocessing complete. Found {len(leaf_values)} leaf values and {len(internal_values)} internal values.")

    # 4. Save the preprocessed artifacts
    base_output_dir = PROJECT_ROOT / "data" / "processed"
    today = datetime.today().strftime('%Y-%m-%d')
    today_folder = datetime.today().strftime('%m-%d')  # Format: MM-DD

    # Create dated folder
    output_dir = base_output_dir / today_folder
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Saving preprocessed data to {output_dir}...")

    # Save marginalization_df
    marginalization_df_name = output_dir / f"{today}_marginalization_df.csv"
    marginalization_df.to_csv(marginalization_df_name)

    # Save parent_child_df
    parent_child_df_name = output_dir / f"{today}_parent_child_df.csv"
    parent_child_df.to_csv(parent_child_df_name)

    # Save exclusion_df
    exclusion_df_name = output_dir / f"{today}_exclusion_df.csv"
    exclusion_df.to_csv(exclusion_df_name)

    # Save mapping_dict
    mapping_dict_name = output_dir / f"{today}_mapping_dict_df.csv"
    mapping_dict_df = pd.DataFrame.from_dict(mapping_dict, orient='index')
    mapping_dict_df.to_csv(mapping_dict_name)

    # Save leaf_values and internal_values
    leaf_values_name = output_dir / f"{today}_leaf_values.pkl"
    internal_values_name = output_dir / f"{today}_internal_values.pkl"
    with open(leaf_values_name, "wb") as fp:
        pickle.dump(leaf_values, fp)
    with open(internal_values_name, "wb") as fp:
        pickle.dump(internal_values, fp)

    print("Pipeline finished successfully.")

if __name__ == "__main__":
    main()