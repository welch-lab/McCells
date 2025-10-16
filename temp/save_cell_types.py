import pandas as pd
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.ontology_utils import load_ontology
from src.data_pipeline.data_loader import load_filtered_cell_metadata

# --- 1. Setup ---
print("Loading ontology...")
cl = load_ontology()
root_cl_id = 'CL:0000988'  # hematopoietic cell

# --- 2. Run metadata filtering to get the cell list ---
print("Filtering cell types from the census... (This may take a moment)")
cell_obs_metadata= load_filtered_cell_metadata(cl, root_cl_id=root_cl_id)

# --- 3. Save the results ---
output_dir = 'data/processed'
os.makedirs(output_dir, exist_ok=True)

if not cell_obs_metadata.empty:
    # Get the unique list of cell type IDs
    target_cell_types = cell_obs_metadata['cell_type_ontology_term_id'].unique().tolist()
    
    # Save the list of cell types to a text file, one ID per line
    file_path = os.path.join(output_dir, 'blood_cell_types_141.txt')
    with open(file_path, 'w') as f:
        for cell_id in target_cell_types:
            f.write(f"{cell_id}\n")
            
    print(f"\nSuccessfully saved {len(target_cell_types)} target cell types to {file_path}")
else:
    print("No cell types found. No file was saved.")
