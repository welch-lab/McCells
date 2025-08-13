import pronto
import pandas as pd
import os
from src.utils.paths import PROJECT_ROOT

def build_ontology_dataframe(ontology):
    """
    Builds a DataFrame representing the ontology hierarchy and a DataFrame for metadata.

    Args:
        ontology (pronto.Ontology): The loaded Cell Ontology.

    Returns:
        tuple: A tuple containing:
            - pd.DataFrame: A DataFrame where the index is parent terms, columns are all
                            terms, and values are 1 if the parent is an ancestor of the
                            column term, 0 otherwise.
            - pd.DataFrame: A DataFrame with columns 'cl_id', 'cl_name', 'cl_idx'
                            mapping CL IDs to names and signed integer indices (positive for leaf, negative for internal).
    """
    print("Extracting all terms from the ontology...")
    all_terms = list(ontology.terms())
    all_term_ids = [term.id for term in all_terms if term.id.startswith("CL:")]

    print(f"Found {len(all_term_ids)} Cell Ontology terms.")

    # Create the empty dataframe for hierarchy
    ontology_df = pd.DataFrame(0, index=all_term_ids, columns=all_term_ids)

    # Create lists to store metadata
    cl_ids = []
    cl_names = []
    cl_indices = []

    print("Populating the ontology DataFrame and collecting metadata. This may take a few minutes...")
    # Start counter from 1 to avoid 0 being neither positive nor negative
    counter = 1
    for term_id in ontology_df.index:
        try:
            term = ontology[term_id]
            cl_ids.append(term.id)
            cl_names.append(term.name)

            # Get all subclasses (descendants) including the term itself
            subclass_ids = {sub.id for sub in term.subclasses(with_self=True)}

            # Determine if it's a leaf node in the full ontology
            # A term is a leaf if it has no subclasses other than itself
            is_leaf = (len(subclass_ids) == 1 and list(subclass_ids)[0] == term.id)

            # Assign signed integer index
            if is_leaf:
                cl_indices.append(counter)
            else:
                cl_indices.append(-counter)
            counter += 1

            # defensive programming in case tree changed but not experiments
            # Find the intersection with columns to populate
            valid_columns = list(subclass_ids.intersection(ontology_df.columns))
            if valid_columns:
                ontology_df.loc[term_id, valid_columns] = 1
        except KeyError:
            print(f"Warning: Term ID {term_id} not found in ontology. Skipping.")

    print("DataFrame population complete.")

    # Create the metadata DataFrame
    ontology_metadata_df = pd.DataFrame({
        'cl_id': cl_ids,
        'cl_name': cl_names,
        'cl_idx': cl_indices
    })
    ontology_metadata_df = ontology_metadata_df.set_index('cl_id') # Set cl_id as index for easy lookup

    return ontology_df, ontology_metadata_df

def main():
    """
    Main function to load the Cell Ontology, process it into DataFrames,
    and save them as Parquet files.
    """
    # Saving inside the project root, in a new 'data/processed' directory
    output_dir = PROJECT_ROOT / "data" / "processed"
    ontology_output_path = output_dir / "ontology.parquet"
    metadata_output_path = output_dir / "ontology_metadata.parquet"

    print("Starting ontology processing.")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # 1. Load the Cell Ontology using pronto
    # This will download 'cl.owl' from the OBO library if not found locally.
    print("Loading Cell Ontology (will download if necessary)...")
    try:
        cl_ontology = pronto.Ontology.from_obo_library('cl.owl')
        print("Ontology loaded successfully.")
    except Exception as e:
        print(f"Failed to load ontology: {e}")
        return

    # 2. Build the DataFrames from the ontology
    ontology_df, ontology_metadata_df = build_ontology_dataframe(cl_ontology)

    # 3. Save the DataFrames to Parquet files
    print(f"\nSaving ontology DataFrame to {ontology_output_path}...")
    ontology_df.to_parquet(ontology_output_path)
    print("Ontology cache saved successfully.")

    print(f"Saving ontology metadata DataFrame to {metadata_output_path}...")
    ontology_metadata_df.to_parquet(metadata_output_path)
    print("Ontology metadata saved successfully.")


if __name__ == "__main__":
    main()
