from src.utils.ontology_utils import load_ontology
from src.data_pipeline.data_loader import load_filtered_cell_metadata

def test_data_loader():
    """
    Tests the functionality of the data_loader module.
    """
    print("Testing the data_loader.py module...")

    # 1. Load the cached ontology object
    cl = load_ontology()
    if cl is None:
        print("Could not load ontology. Aborting test.")
        return

    # Define the root of the ontology subgraph to be processed
    root_cl_id = 'CL:0000988'  # hematopoietic cell

    # 2. Load filtered cell metadata with a small min_cell_count for speed
    print("Calling load_filtered_cell_metadata with min_cell_count=100...")
    cell_obs_metadata = load_filtered_cell_metadata(cl, root_cl_id=root_cl_id, min_cell_count=100)

    if cell_obs_metadata.empty:
        print("No cell metadata loaded. The function is callable but returned no data with the current filters.")
    else:
        print("\nSuccessfully loaded cell metadata. The data_loader.py module is functional.")
        print("Here is the head of the returned dataframe:")
        print(cell_obs_metadata.head())

if __name__ == "__main__":
    test_data_loader()
