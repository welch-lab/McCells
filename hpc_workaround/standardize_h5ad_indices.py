import scanpy as sc
import glob
import os


H5AD_DIR = "/scratch/sigbio_project_root/sigbio_project25/jingqiao/mccell-singleseq"

# The desired, consistent name for the observation (cell) index
TARGET_OBS_INDEX_NAME = "cell_id"

# The desired, consistent name for the variable (gene) index
TARGET_VAR_INDEX_NAME = "var_id"


def standardize_h5ad_indices():
    """
    Iterates through H5AD files to ensure obs and var indices have consistent names.
    This is a preprocessing step to fix inconsistencies across files.
    """
    h5ad_files = glob.glob(os.path.join(H5AD_DIR, "*.h5ad"))

    if not h5ad_files:
        print(f"No H5AD files found in {H5AD_DIR}")
        return

    print(f"Found {len(h5ad_files)} H5AD files to check and standardize.")

    for h5ad_file in h5ad_files:
        print(f"--- Processing {os.path.basename(h5ad_file)} ---")
        try:
            adata = sc.read_h5ad(h5ad_file)
            modified = False

            # 1. Standardize observation (cell) index name
            if adata.obs.index.name != TARGET_OBS_INDEX_NAME:
                print(f"  Renaming obs index from '{adata.obs.index.name}' to '{TARGET_OBS_INDEX_NAME}'")
                adata.obs.index.name = TARGET_OBS_INDEX_NAME
                modified = True

            # 2. Standardize variable (gene) index name
            if adata.var.index.name != TARGET_VAR_INDEX_NAME:
                print(f"  Renaming var index from '{adata.var.index.name}' to '{TARGET_VAR_INDEX_NAME}'")
                adata.var.index.name = TARGET_VAR_INDEX_NAME
                modified = True

            # 3. Write back to the file only if changes were made
            if modified:
                print(f"  Saving standardized file...")
                adata.write_h5ad(h5ad_file)
                print(f"  Done.")
            else:
                print("  Indices already correct. No changes needed.")

        except Exception as e:
            print(f"  ERROR processing file: {e}")

    print("\nStandardization process complete.")


if __name__ == "__main__":
    standardize_h5ad_indices()