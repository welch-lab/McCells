import cellxgene_census
import pandas as pd
from src.utils.ontology_utils import get_sub_DAG

def load_filtered_cell_metadata(cl, root_cl_id: str, min_cell_count: int = 5000) -> tuple[pd.DataFrame, str]:
    """
    Loads cell metadata from the CellXGene Census in a memory-efficient way.
    Filters for descendants of a given root CL ID with a minimum count.
    Returns the filtered metadata and the filter string for reuse.
    """
    print(f"Fetching descendants of {root_cl_id}...")
    descendant_cell_types = {sub.id for sub in get_sub_DAG(cl, root_cl_id)}

    if not descendant_cell_types:
        print(f"No descendants found for {root_cl_id}. Aborting.")
        return pd.DataFrame(), ""

    print("Connecting to CellXGene Census...")
    with cellxgene_census.open_soma() as census:
        experiment = census["census_data"]["homo_sapiens"]

        # Memory-efficiently count cell types directly from the census
        print("Counting cell types in the census...")
        cell_type_counts = experiment.obs.count(
            "cell_type_ontology_term_id",
            value_filter=f"cell_type_ontology_term_id in {list(descendant_cell_types)}"
        )

        # Filter for cell types with a minimum count
        valid_cell_types = [
            cell_type for cell_type, count in cell_type_counts.items() if count > min_cell_count
        ]

        print(f"Found {len(valid_cell_types)} cell types with > {min_cell_count} cells.")

        if not valid_cell_types:
            print("No cell types matching the criteria. Aborting.")
            return pd.DataFrame(), ""

        # Build the value filter for the final query
        obs_val_filter = f'''assay == "10x 3' v3" and is_primary_data == True and cell_type_ontology_term_id in {valid_cell_types}'''

        # Query for the final cell metadata using the generated filter
        print("Querying for final cell metadata...")
        cell_obs_metadata = (
            experiment.obs.read(
                value_filter=obs_val_filter,
                column_names=['cell_type_ontology_term_id']
            ).concat().to_pandas()
        )

    print("Finished loading and filtering cell metadata.")
    return cell_obs_metadata, obs_val_filter
