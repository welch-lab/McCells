"""
Pre-compute highly variable genes and save to disk.
Run this once locally, then load the saved gene list in training.
"""
import pandas as pd
import pickle
from pathlib import Path
import cellxgene_census
from cellxgene_census.experimental.pp import get_highly_variable_genes
from src.utils.paths import PROJECT_ROOT

# Load the preprocessed data to get cell types
DATE = '2025-10-17'
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

print(f"Loading mapping dict from: {PROCESSED_DATA_DIR}")
mapping_dict_df = pd.read_csv(PROCESSED_DATA_DIR / f"{DATE}_mapping_dict_df.csv", index_col=0)
mapping_dict = pd.Series(mapping_dict_df.iloc[:, 0].values, index=mapping_dict_df.index).to_dict()
all_cell_values = list(mapping_dict.keys())

print(f"Computing HVGs for {len(all_cell_values)} cell types...")
print("This may take 2-5 minutes...")

# Compute HVGs from online census
with cellxgene_census.open_soma(census_version="2025-01-30") as census:
    obs_value_filter = f"assay == '10x 3\\' v3' and is_primary_data == True and cell_type_ontology_term_id in {all_cell_values}"

    hvg_df = get_highly_variable_genes(
        census,
        organism="Homo sapiens",
        obs_value_filter=obs_value_filter,
        n_top_genes=2000,
        batch_key="dataset_id"
    )

print(f"Computed {len(hvg_df)} highly variable genes")

# Save the HVG dataframe and gene list
hvg_output_path = PROCESSED_DATA_DIR / f"{DATE}_hvg_2000.csv"
gene_list_output_path = PROCESSED_DATA_DIR / f"{DATE}_gene_list_2000.pkl"

hvg_df.to_csv(hvg_output_path)
print(f"Saved HVG dataframe to: {hvg_output_path}")

gene_list = hvg_df["feature_id"].tolist()
with open(gene_list_output_path, "wb") as fp:
    pickle.dump(gene_list, fp)
print(f"Saved gene list to: {gene_list_output_path}")

print("\nDone! You can now load this gene list in your training notebook.")
