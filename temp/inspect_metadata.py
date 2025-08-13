import pandas as pd
import os

# Construct the absolute path to the project root dynamically
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Assuming this script is in temp/, and real_McCell is a sibling
parent_dir = os.path.dirname(current_script_dir)
project_root = os.path.join(parent_dir, "real_McCell")

metadata_path = os.path.join(project_root, "data", "processed", "ontology_metadata.parquet")

try:
    ontology_metadata_df = pd.read_parquet(metadata_path)
    print("Successfully loaded ontology_metadata.parquet")
    print("\nDataFrame Head:")
    print(ontology_metadata_df.head())

    print("\nDataFrame Info:")
    ontology_metadata_df.info()

    print("\nExamples of cl_idx values (positive for leaf, negative for internal):")
    # Get some positive (leaf) indices
    positive_indices = ontology_metadata_df[ontology_metadata_df['cl_idx'] > 0].head(5)
    print("\nPositive cl_idx (Leaf Nodes):")
    print(positive_indices[['cl_name', 'cl_idx']])

    # Get some negative (internal) indices
    negative_indices = ontology_metadata_df[ontology_metadata_df['cl_idx'] < 0].head(5)
    print("\nNegative cl_idx (Internal Nodes):")
    print(negative_indices[['cl_name', 'cl_idx']])

except FileNotFoundError:
    print(f"Error: Ontology metadata file not found at {metadata_path}. Please ensure build_ontology_cache.py has been run.")
except Exception as e:
    print(f"An error occurred: {e}")
