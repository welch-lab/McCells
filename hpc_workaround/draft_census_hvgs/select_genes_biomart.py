"""
Select 2000 protein-coding genes from BioMart export.
Fast, works offline, no S3 dependencies.
"""
import pandas as pd
import pickle
from pathlib import Path
from src.utils.paths import PROJECT_ROOT, get_data_folder

# Paths
BIOMART_FILE = PROJECT_ROOT / "hpc_workaround/data/mart_export.txt"
DATE = '2025-10-24'
PROCESSED_DATA_DIR = get_data_folder(DATE)

print("=" * 60)
print("Selecting 2000 protein-coding genes from BioMart")
print("=" * 60)

print(f"\nReading BioMart gene list from: {BIOMART_FILE}")
biomart = pd.read_csv(BIOMART_FILE)

print(f"Total genes in BioMart: {len(biomart)}")
print(f"\nGene types:")
for gene_type, count in biomart['Gene type'].value_counts().head(10).items():
    print(f"  {gene_type}: {count}")

# Filter for protein-coding genes only
coding_only = biomart[biomart['Gene type'] == 'protein_coding']
print(f"\nProtein-coding genes: {len(coding_only)}")

# Select first 2000 protein-coding genes
num_genes = 2000
gene_list = coding_only['Gene stable ID'].tolist()[:num_genes]

print(f"Selected {len(gene_list)} protein-coding genes")

# Save gene list (matching the HVG filename pattern)
gene_list_output_path = PROCESSED_DATA_DIR / f"{DATE}_gene_list_2000.pkl"
with open(gene_list_output_path, "wb") as fp:
    pickle.dump(gene_list, fp)

print(f"\n✓ Saved gene list to: {gene_list_output_path}")
print("\nDone! Your training notebook will load this file automatically.")
print(f"\nFirst 10 genes: {gene_list[:10]}")
print(f"Last 10 genes: {gene_list[-10:]}")
