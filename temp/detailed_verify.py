import pandas as pd
import pronto

def verify_hierarchy():
    """
    Performs a detailed check on the ontology DataFrame to ensure a specific
    parent-child relationship is correctly encoded.
    """
    parquet_path = 'data/processed/ontology.parquet'
    child_id = 'CL:0000625'  # CD8-positive, alpha-beta T cell

    print("--- Detailed Hierarchy Verification ---")

    try:
        # 1. Load the DataFrame
        print(f"Reading {parquet_path}...")
        ontology_df = pd.read_parquet(parquet_path)
        print("DataFrame loaded.")

        # 2. Load the ontology to find relationships
        print("Loading Cell Ontology (may use cache)...")
        cl = pronto.Ontology.from_obo_library('cl.owl')
        print("Ontology loaded.")

        # 3. Get the specific child term and its parent
        child_term = cl[child_id]
        parent_term = next(child_term.superclasses(distance=1, with_self=False))
        parent_id = parent_term.id

        print(f'\nVerification Target: \'{child_term.name}\' ({child_id})')
        print(f'Its parent is: \'{parent_term.name}\' ({parent_id})')

        # 4. Get all children of that parent
        sibling_terms = list(parent_term.subclasses(distance=1, with_self=False))
        sibling_ids = [term.id for term in sibling_terms]
        print(f'The parent has {len(sibling_ids)} children (siblings of the target).')

        # 5. Check the values in the DataFrame
        print(f'\nChecking the row for parent \'{parent_id}\' against its children columns...')
        
        # Filter for only those children that exist in our DataFrame
        valid_sibling_ids = [sid for sid in sibling_ids if sid in ontology_df.columns]
        
        parent_slice = ontology_df.loc[parent_id, valid_sibling_ids]

        print("\n--- Verification Results ---")
        print(parent_slice)

        if parent_slice.all():
            print('\nSUCCESS: All children are correctly marked as 1.')
        else:
            print('\nFAILURE: Some children are not marked as 1.')

    except Exception as e:
        print(f'\nAn error occurred: {e}')

if __name__ == "__main__":
    verify_hierarchy()
