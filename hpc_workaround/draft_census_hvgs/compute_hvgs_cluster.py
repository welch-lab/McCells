"""
Compute highly variable genes on cluster.
Tests S3 connectivity first, then computes HVGs.
"""
import pandas as pd
import pickle
import socket
import sys
from pathlib import Path
from datetime import datetime

# Test S3 connectivity first
print("=" * 60)
print("Testing S3 Connectivity...")
print("=" * 60)

s3_hosts = [
    "cellxgene-census-public-us-west-2.s3.us-west-2.amazonaws.com",
    "s3-us-west-2.amazonaws.com",
    "s3.us-west-2.amazonaws.com"
]

connectivity_ok = False
for host in s3_hosts:
    try:
        print(f"Resolving {host}...", end=" ")
        ip = socket.gethostbyname(host)
        print(f"✓ {ip}")
        connectivity_ok = True
    except socket.gaierror as e:
        print(f"✗ Failed: {e}")

if not connectivity_ok:
    print("\n❌ ERROR: Cannot resolve S3 hostnames!")
    print("Your cluster likely blocks S3 access.")
    print("Use BioMart gene selection instead (select_genes_biomart.py)")
    sys.exit(1)

print("\n✓ S3 connectivity looks good! Proceeding...\n")

# Now import the heavy libraries
print("Loading libraries...")
import cellxgene_census
from cellxgene_census.experimental.pp import get_highly_variable_genes

# Setup paths
from src.utils.paths import get_data_folder
DATE = '2025-10-24'
PROCESSED_DATA_DIR = get_data_folder(DATE)

print(f"Loading mapping dict from: {PROCESSED_DATA_DIR}")
mapping_dict_df = pd.read_csv(PROCESSED_DATA_DIR / f"{DATE}_mapping_dict_df.csv", index_col=0)
mapping_dict = pd.Series(mapping_dict_df.iloc[:, 0].values, index=mapping_dict_df.index).to_dict()
all_cell_values = list(mapping_dict.keys())

print(f"\nComputing HVGs for {len(all_cell_values)} cell types...")
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("This may take 5-10 minutes...\n")

try:
    # Compute HVGs from online census
    print("Opening Census...")
    with cellxgene_census.open_soma(census_version="2025-01-30") as census:
        print("Building query filter...")
        obs_value_filter = f"assay == '10x 3\\' v3' and is_primary_data == True and cell_type_ontology_term_id in {all_cell_values}"

        print("Computing highly variable genes...")
        print("(This step reads expression data from S3 - be patient)")

        hvg_df = get_highly_variable_genes(
            census,
            organism="Homo sapiens",
            obs_value_filter=obs_value_filter,
            n_top_genes=2000,
            batch_key="dataset_id"
        )

    print(f"\n✓ Computed {len(hvg_df)} highly variable genes!")

    # Save the HVG dataframe and gene list
    hvg_output_path = PROCESSED_DATA_DIR / f"{DATE}_hvg_2000.csv"
    gene_list_output_path = PROCESSED_DATA_DIR / f"{DATE}_gene_list_2000.pkl"

    hvg_df.to_csv(hvg_output_path)
    print(f"✓ Saved HVG dataframe to: {hvg_output_path}")

    gene_list = hvg_df["feature_id"].tolist()
    with open(gene_list_output_path, "wb") as fp:
        pickle.dump(gene_list, fp)
    print(f"✓ Saved gene list to: {gene_list_output_path}")

    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✓ SUCCESS! You can now use these HVGs in training.")
    print(f"\nFirst 10 genes: {gene_list[:10]}")

except Exception as e:
    print(f"\n❌ ERROR during HVG computation:")
    print(f"   {type(e).__name__}: {e}")
    print("\nIf this is a network/timeout error, try:")
    print("  1. Using a compute node with internet access")
    print("  2. Using BioMart gene selection instead")
    sys.exit(1)
