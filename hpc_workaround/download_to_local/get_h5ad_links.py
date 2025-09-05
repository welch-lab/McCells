import cellxgene_census
import pandas as pd
import os
import time

def get_h5ad_links():
    """
    This script fetches the download links for the newest Homo sapiens single-cell
    sequence data sets from the CELLxGENE Discover Dataset Schemas, filtered by
    assay and primary data status, and saves them to a file.
    """
    output_filename = "h5ad_links.txt"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filepath = os.path.join(script_dir, output_filename)

    print("Opening the latest census...")
    with cellxgene_census.open_soma(census_version="latest") as census:
        experiment = census["census_data"]["homo_sapiens"]

        print("Reading metadata to filter datasets...")
        obs_df = experiment.obs.read(
            value_filter='assay == "10x 3\\' v3" and is_primary_data == True',
            column_names=["dataset_id", "assay", "is_primary_data"]
        ).concat().to_pandas()

        if obs_df.empty:
            print("No datasets found matching the criteria.")
            return

        dataset_ids = obs_df["dataset_id"].unique()
        print(f"Found {len(dataset_ids)} matching datasets.")
        print(f"Fetching H5AD file URIs and writing to {output_filename}...")

        with open(output_filepath, "w") as f:
            for i, dataset_id in enumerate(dataset_ids):
                print(f"Processing dataset {i+1}/{len(dataset_ids)}: {dataset_id}")
                retries = 3
                while retries > 0:
                    try:
                        uri_info = cellxgene_census.get_source_h5ad_uri(dataset_id)
                        link = uri_info['uri']
                        print(f"  -> Found link: {link}")
                        f.write(link + '\n')
                        break # Success, exit while loop
                    except Exception as e:
                        print(f"  -> Could not retrieve URI for dataset {dataset_id}: {e}")
                        retries -= 1
                        if retries > 0:
                            print("  -> Retrying...")
                            time.sleep(5) # wait 5 seconds before retrying
                        else:
                            print(f"  -> Failed to retrieve URI for dataset {dataset_id} after multiple retries.")
        
        print(f"Successfully wrote URIs to {output_filepath}")

if __name__ == "__main__":
    get_h5ad_links()
