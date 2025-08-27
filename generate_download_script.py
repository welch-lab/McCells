
import cellxgene_census

def generate_download_script():
    """
    This script generates a shell script to download all human datasets from the Cellxgene Census.
    """
    with cellxgene_census.open_soma() as census:
        dataset_ids = census["census_data"]["homo_sapiens"].ms["RNA"].var.read(value_filter="feature_id in ['ENSG00000163599']").concat().to_pandas()["dataset_id"].unique()

    with open("download_data.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("set -e\n\n")
        for dataset_id in dataset_ids:
            try:
                uri = cellxgene_census.get_source_h5ad_uri(dataset_id)["uri"]
                f.write(f"wget {uri} -O {dataset_id}.h5ad\n")
            except Exception as e:
                print(f"Could not get URI for dataset {dataset_id}: {e}")

if __name__ == "__main__":
    generate_download_script()
