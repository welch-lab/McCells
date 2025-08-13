import pandas as pd
from src.utils.paths import PROJECT_ROOT

def get_sub_DAG(cl_number: str) -> set:
    """
    Given a CL number, loads the ontology DataFrame from 'data/processed/ontology.parquet'
    and returns a set of all its downstream nodes (descendants), including the CL number itself
    if it exists in the DataFrame.

    Args:
        cl_number (str): The CL number (e.g., "CL:0000000") for which to find descendants.

    Returns:
        set: A set of CL numbers representing all downstream nodes (descendants) of the given cl_number.
             Returns an empty set if the cl_number is not found in the ontology DataFrame.
    """
    ontology_path = PROJECT_ROOT / "data" / "processed" / "ontology.parquet"

    try:
        ontology_df = pd.read_parquet(ontology_path)
    except FileNotFoundError:
        print(f"Error: Ontology file not found at {ontology_path}. Please ensure it has been built.")
        return set()

    if cl_number not in ontology_df.index:
        return set()

    descendants = ontology_df.loc[cl_number][ontology_df.loc[cl_number] == 1].index.tolist()

    return set(descendants)

def get_cell_info(cl_ids):
    """
    Given a CL ID or a list of CL IDs, this function returns a DataFrame with their
    information (cl_id, cl_name, cl_idx).

    Args:
        cl_ids (str or list): A single CL ID (e.g., "CL:0000988") or a list of CL IDs.

    Returns:
        pd.DataFrame: A DataFrame containing the information for the requested CL IDs.
                      Returns an empty DataFrame if the metadata file is not found or
                      none of the requested CL IDs are in the metadata.
    """
    metadata_path = PROJECT_ROOT / "data" / "processed" / "ontology_metadata.parquet"

    try:
        metadata_df = pd.read_parquet(metadata_path)
    except FileNotFoundError:
        print(f"Error: Ontology metadata file not found at {metadata_path}. Please ensure it has been built.")
        return pd.DataFrame()

    if isinstance(cl_ids, str):
        cl_ids = [cl_ids]

    return metadata_df[metadata_df.index.isin(cl_ids)]