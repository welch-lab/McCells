import tiledbsoma
import tiledbsoma.io
import os
import glob

# --- Configuration ---
# The directory where you downloaded the H5AD files
H5AD_DIR = "/scratch/sigbio_project_root/sigbio_project25/jingqiao/mccell-singleseq"

# The URI for the new SOMA Experiment that will be created
EXPERIMENT_URI = os.path.join(H5AD_DIR, "soma_experiment")

# The name of the measurement to store the data in
MEASUREMENT_NAME = "RNA"

def ingest_h5ad_files():
    """
    Ingests a directory of H5AD files into a single TileDB-SOMA Experiment.
    """
    h5ad_files = glob.glob(os.path.join(H5AD_DIR, "*.h5ad"))[:2]
    
    if not h5ad_files:
        print(f"No H5AD files found in {H5AD_DIR}")
        return

    print(f"Found {len(h5ad_files)} H5AD files to ingest.")

    # 1. Register all H5AD files to create a unified schema
    # This will create new 'cell_id' and 'gene_id' columns in the SOMA experiment
    # based on the index of each H5AD file.
    print("Registering H5AD files...")
    registration_mapping = tiledbsoma.io.register_h5ads(
        EXPERIMENT_URI,
        h5ad_file_names=h5ad_files,
        measurement_name=MEASUREMENT_NAME,
        obs_field_name="cell_id",
        var_field_name="gene_id",
        append_obsm_varm=True,
    )

    # 2. Ingest each H5AD file into the SOMA Experiment
    print("Ingesting H5AD files...")
    for h5ad_file in h5ad_files:
        print(f"  -> Ingesting {os.path.basename(h5ad_file)}")
        tiledbsoma.io.from_h5ad(
            EXPERIMENT_URI,
            h5ad_file,
            measurement_name=MEASUREMENT_NAME,
            ingest_mode="write",
            registration_mapping=registration_mapping,
        )

    print(f"\nSuccessfully ingested {len(h5ad_files)} H5AD files into {EXPERIMENT_URI}")

    # --- Verify the result ---
    with tiledbsoma.open(EXPERIMENT_URI) as exp:
        print("\nExperiment summary:")
        print(exp)
        print("\nobs dataframe:")
        print(exp.obs.read().concat().to_pandas().info())
        print("\nvar dataframe:")
        print(exp.ms[MEASUREMENT_NAME].var.read().concat().to_pandas().info())

if __name__ == "__main__":
    ingest_h5ad_files()
