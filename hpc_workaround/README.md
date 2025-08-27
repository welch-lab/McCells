# HPC Data Download and Filtering Script

This directory contains a Python script (`download_and_filter_data.py`) designed to download and filter single-cell sequencing data from the CELLxGENE Census directly on an HPC login node.

## `download_and_filter_data.py`

This script performs the following actions:

1.  **Connects to the CELLxGENE Census:** It uses the `cellxgene-census` library to access the human single-cell data.
2.  **Applies Filters:**
    *   **Genes:** It filters for **protein-coding genes only**. This requires `mart_export.txt` to be present in the same directory.
    *   **Cell Types:** It identifies cell types that have **more than 5000 cells** in the Census and are present in a predefined list (`cell_type_list_full.txt`). This requires `cell_type_list_full.txt` to be present in the same directory.
    *   **Assay:** It filters for data generated using the **"10x 3' v3" assay**.
    *   **Primary Data:** It includes only **primary data** (`is_primary_data == True`).
3.  **Batches Data Retrieval:** To manage memory efficiently, the script divides the filtered cell types into batches. It then queries the Census for each batch separately.
4.  **Downloads to Local Memory:** For each batch, the script downloads the corresponding `AnnData` object directly to the cluster's local memory (the directory where the script is run). The data is saved as gzipped `.h5ad` files (e.g., `filtered_data_batch_1.h5ad`).

## How to Run

1.  **Ensure Dependencies:** Make sure you have `cellxgene-census`, `tiledbsoma`, `pandas`, and `numpy` installed in your Python environment on the HPC login node.
2.  **Place Input Files:** Ensure `mart_export.txt` and `cell_type_list_full.txt` are in the same directory as `download_and_filter_data.py`.
3.  **Execute the Script:** Run the script directly from your HPC login node:
    ```bash
    python download_and_filter_data.py
    ```

This will create multiple `filtered_data_batch_X.h5ad` files in the specified output directory: /nfs/turbo/umms-welchjd/single-cells-data, each containing a subset of the filtered single-cell data.