import pandas as pd
import os
import sys

# Add the project root to the Python path to allow importing from src.utils
current_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_script_dir) # This should be /mnt/c/Users/zhaoj/projects/
project_root = os.path.join(parent_dir, "real_McCell") # This should be /mnt/c/Users/zhaoj/projects/real_McCell
sys.path.insert(0, project_root)

from src.utils.ontology_utils import get_sub_DAG

# --- Load ontology_df once ---
ontology_path = os.path.join(project_root, "data", "processed", "ontology.parquet")
try:
    ontology_df = pd.read_parquet(ontology_path)
except FileNotFoundError:
    print(f"Error: Ontology file not found at {ontology_path}. Please ensure it has been built.")
    sys.exit(1)
# ----------------------------

hematopoietic_cl_id = "CL:0000988"

print(f"Getting all descendants for {hematopoietic_cl_id}...")
# Call get_sub_DAG once to get all descendants
all_hematopoietic_descendants = get_sub_DAG(hematopoietic_cl_id)

if not all_hematopoietic_descendants:
    print(f"No descendants found for {hematopoietic_cl_id}.")
else:
    print(f"Found {len(all_hematopoietic_descendants)} descendants (including itself).")

    leaf_nodes = set()
    internal_nodes = set()

    # Classify leaf and internal nodes using the loaded ontology_df
    for cl_id in all_hematopoietic_descendants:
        # A node is an internal node if it has any descendant (other than itself) within the sub-DAG
        # We check if cl_id is an ancestor of any other node in all_hematopoietic_descendants
        is_internal = False
        if cl_id in ontology_df.index: # Ensure cl_id is an ancestor in the ontology_df
            # Get all descendants of the current cl_id from the pre-loaded ontology_df
            current_cl_descendants = set(ontology_df.loc[cl_id][ontology_df.loc[cl_id] == 1].index.tolist())

            # Check if any of these descendants (excluding cl_id itself) are also in all_hematopoietic_descendants
            # This means it has children within the hematopoietic sub-DAG
            if any(desc != cl_id and desc in all_hematopoietic_descendants for desc in current_cl_descendants):
                is_internal = True

        if is_internal:
            internal_nodes.add(cl_id)
        else:
            leaf_nodes.add(cl_id)

    print("\nLeaf Nodes (hematopoietic sub-DAG):")
    for node in sorted(list(leaf_nodes)):
        print(node)

    print("\nInternal Nodes (hematopoietic sub-DAG):")
    for node in sorted(list(internal_nodes)):
        print(node)
