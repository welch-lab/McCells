from src.utils.ontology_utils import load_ontology
from src.data_pipeline.data_loader import load_filtered_cell_metadata

def main():
    cl = load_ontology()
    if cl is None:
        return

    print("--- Testing data_loader.py ---")
    cell_metadata = load_filtered_cell_metadata(cl, 'CL:0000988')

    if not cell_metadata.empty:
        print("\n--- Data Loader Output ---")
        print(cell_metadata.head())
        print(f"\nShape of the returned DataFrame: {cell_metadata.shape}")
    else:
        print("Data loader returned an empty DataFrame.")

if __name__ == "__main__":
    main()

