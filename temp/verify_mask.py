import torch
import pickle
import pandas as pd
from src.utils.ontology_utils import load_ontology
from src.utils.paths import PROJECT_ROOT

def main():
    # Load all the necessary files
    output_dir = PROJECT_ROOT / "data" / "processed"
    today = "2025-08-13"

    print("--- Loading Artifacts ---")
    cl = load_ontology()
    if cl is None:
        return

    mask = torch.load(output_dir / f"{today}_cell_parent_mask.pt")
    ontology_df = pd.read_csv(output_dir / f"{today}_ontology_df.csv", index_col=0)
    with open(output_dir / f"{today}_leaf_values.pkl", "rb") as f:
        leaf_values = pickle.load(f)
    with open(output_dir / f"{today}_internal_values.pkl", "rb") as f:
        internal_values = pickle.load(f)

    all_cell_types = leaf_values + internal_values
    parent_nodes = ontology_df.index.tolist()

    print(f"Mask shape: {mask.shape}")
    print(f"Number of parent nodes (rows): {len(parent_nodes)}")
    print(f"Number of cell types (columns): {len(all_cell_types)}")

    # --- Verification Step 1: Leaf Node ---
    print("\n--- Verifying a Leaf Node ---")
    leaf_to_check_id = leaf_values[0]
    leaf_to_check_name = cl[leaf_to_check_id].name
    leaf_column_index = all_cell_types.index(leaf_to_check_id)
    leaf_column = mask[:, leaf_column_index]

    print(f"Checking leaf node: {leaf_to_check_name} ({leaf_to_check_id})")
    is_all_ones = torch.all(leaf_column == 1).item()
    print(f"Is the column for this leaf node all 1s? {is_all_ones}")
    if not is_all_ones:
        print("Verification FAILED: Leaf node column should be all 1s.")
    else:
        print("Verification PASSED.")

    # --- Verification Step 2: Internal Node ---
    print("\n--- Verifying an Internal Node ---")
    internal_to_check_id = 'CL:0000542' # lymphocyte, a well-known internal node
    if internal_to_check_id not in internal_values:
        print(f"Could not perform check, {internal_to_check_id} not in internal_values list.")
        return
        
    internal_to_check_name = cl[internal_to_check_id].name
    internal_column_index = all_cell_types.index(internal_to_check_id)
    internal_column = mask[:, internal_column_index]

    print(f"Checking internal node: {internal_to_check_name} ({internal_to_check_id})")

    # Get all descendants of this internal node from the ontology
    descendants = {term.id for term in cl[internal_to_check_id].subclasses(with_self=True)}

    # Check the logic
    verification_passed = True
    for i, parent_id in enumerate(parent_nodes):
        mask_value = internal_column[i].item()
        # If the parent is a descendant of the internal node, the mask should be 0
        if parent_id in descendants:
            if mask_value != 0:
                print(f"Verification FAILED for parent {cl[parent_id].name} ({parent_id})")
                print(f"It is a descendant, so mask value should be 0, but it is {mask_value}")
                verification_passed = False
        # If the parent is NOT a descendant, the mask should be 1
        else:
            if mask_value != 1:
                print(f"Verification FAILED for parent {cl[parent_id].name} ({parent_id})")
                print(f"It is NOT a descendant, so mask value should be 1, but it is {mask_value}")
                verification_passed = False

    if verification_passed:
        print("Verification PASSED.")

if __name__ == "__main__":
    main()
