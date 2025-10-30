#!/usr/bin/env python
"""
Verification script to diagnose why local SOMA database has only ~24k cells
instead of expected ~6.3M cells.

This script should be run on the Great Lakes cluster to check:
1. Total cells in the local SOMA database
2. Cell counts after applying filters
3. Comparison with expected counts from remote Census
"""

import tiledbsoma as soma
import pandas as pd
from pathlib import Path

# Configuration
SOMA_PATH = "/scratch/sigbio_project_root/sigbio_project25/jingqiao/mccell-single/soma_db_homo_sapiens"

print("=" * 80)
print("SOMA DATABASE VERIFICATION SCRIPT")
print("=" * 80)
print(f"\nLocal SOMA path: {SOMA_PATH}")

# Check if path exists
if not Path(SOMA_PATH).exists():
    print(f"\n❌ ERROR: SOMA database path does not exist!")
    print(f"   Path: {SOMA_PATH}")
    exit(1)

print(f"✓ Path exists")

# Open the SOMA database
print(f"\nOpening SOMA database...")
try:
    experiment = soma.open(SOMA_PATH, mode="r")
    print("✓ Successfully opened SOMA database")
except Exception as e:
    print(f"❌ ERROR opening SOMA database: {e}")
    exit(1)

# Test 1: Check total number of observations (cells)
print("\n" + "=" * 80)
print("TEST 1: Total Cells in Database")
print("=" * 80)

try:
    # Count cells by reading soma_joinid
    print("Counting total cells...")
    obs_count_df = experiment.obs.read(column_names=["soma_joinid"]).concat().to_pandas()
    total_cells = len(obs_count_df)
    print(f"Total cells in database: {total_cells:,}")
    del obs_count_df  # Free memory

except Exception as e:
    print(f"❌ ERROR counting cells: {e}")
    total_cells = None

# Test 2: Read first few cells to check structure
print("\n" + "=" * 80)
print("TEST 2: Sample Data Structure")
print("=" * 80)

try:
    print("\nReading first 10 cells...")
    obs_sample = experiment.obs.read(coords=(slice(10),)).concat().to_pandas()
    print(f"\nColumns available in obs:")
    print(obs_sample.columns.tolist())
    print(f"\nFirst 3 cells:")
    print(obs_sample.head(3))

except Exception as e:
    print(f"❌ ERROR reading sample data: {e}")

# Test 3: Check assay distribution
print("\n" + "=" * 80)
print("TEST 3: Assay Distribution")
print("=" * 80)

try:
    # Try to read all assay values (might be memory intensive if database is large)
    print("\nReading assay column...")
    if total_cells and total_cells > 100000:
        print(f"⚠️  Database has {total_cells:,} cells - reading assay column may take time...")

    obs_assay = experiment.obs.read(column_names=["assay"]).concat().to_pandas()
    assay_counts = obs_assay['assay'].value_counts()

    print(f"\nAssay distribution (top 10):")
    print(assay_counts.head(10))

    # Check for 10x 3' v3
    if "10x 3' v3" in assay_counts.index:
        v3_count = assay_counts["10x 3' v3"]
        print(f"\n✓ Found '10x 3' v3' assay: {v3_count:,} cells")
    else:
        print(f"\n❌ WARNING: '10x 3' v3' assay NOT found in database!")
        print(f"   Available assays: {assay_counts.index.tolist()[:5]}")

    del obs_assay  # Free memory

except Exception as e:
    print(f"❌ ERROR reading assay distribution: {e}")

# Test 4: Check is_primary_data distribution
print("\n" + "=" * 80)
print("TEST 4: Primary Data Distribution")
print("=" * 80)

try:
    print("\nReading is_primary_data column...")
    obs_primary = experiment.obs.read(column_names=["is_primary_data"]).concat().to_pandas()
    primary_counts = obs_primary['is_primary_data'].value_counts()

    print(f"\nis_primary_data distribution:")
    print(primary_counts)

    if True in primary_counts.index:
        primary_true_count = primary_counts[True]
        print(f"\n✓ Primary data cells: {primary_true_count:,}")
    else:
        print(f"\n❌ WARNING: No primary data cells found!")

    del obs_primary  # Free memory

except Exception as e:
    print(f"❌ ERROR reading is_primary_data: {e}")

# Test 5: Apply the actual filter used in training
print("\n" + "=" * 80)
print("TEST 5: Filter Applied in Training")
print("=" * 80)

try:
    # This is a simplified filter - just assay and primary data (no cell types)
    filter_str = 'assay == "10x 3\' v3" and is_primary_data == True'
    print(f"\nApplying filter: {filter_str}")

    with experiment.axis_query(
        measurement_name="RNA",
        obs_query=soma.AxisQuery(value_filter=filter_str),
    ) as query:
        # Count matching cells
        filtered_obs = query.obs().concat().to_pandas()
        filtered_count = len(filtered_obs)

        print(f"\n✓ Cells matching filter: {filtered_count:,}")

        if filtered_count < 1000000:
            print(f"\n⚠️  WARNING: Expected millions of cells, but only found {filtered_count:,}")
            print(f"   This suggests the downloaded SOMA database is incomplete or incorrect!")
        else:
            print(f"\n✓ Cell count looks reasonable")

        # Check unique cell types
        if 'cell_type_ontology_term_id' in filtered_obs.columns:
            unique_cell_types = filtered_obs['cell_type_ontology_term_id'].nunique()
            print(f"   Unique cell types: {unique_cell_types}")

            cell_type_counts = filtered_obs['cell_type_ontology_term_id'].value_counts()
            print(f"\n   Top 10 cell types:")
            print(cell_type_counts.head(10))

except Exception as e:
    print(f"❌ ERROR applying filter: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Check var (genes)
print("\n" + "=" * 80)
print("TEST 6: Gene/Feature Information")
print("=" * 80)

try:
    var_shape = experiment.ms['RNA'].var.shape
    print(f"var.shape: {var_shape}")
    print(f"Total features/genes: {var_shape[0]:,}")

    # Sample some genes
    var_sample = experiment.ms['RNA'].var.read(coords=(slice(5),)).concat().to_pandas()
    print(f"\nSample genes:")
    print(var_sample)

except Exception as e:
    print(f"❌ ERROR reading var: {e}")

# Close the experiment
print("\n" + "=" * 80)
print("CLEANUP")
print("=" * 80)

try:
    experiment.close()
    print("✓ Closed SOMA database")
except Exception as e:
    print(f"⚠️  Warning closing database: {e}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
Expected behavior (from diagnose_cell_counts.ipynb):
- Total cells with '10x 3' v3' + primary: ~31.8M cells
- After filtering to 80 specific cell types: ~6.3M cells

If your local database shows significantly fewer cells (e.g., ~24k), then:
1. The download did not complete successfully
2. The download script downloaded the wrong data/subset
3. The SOMA database is corrupted

Next steps:
- If cell count is low: Re-run the download script (download_soma.sh)
- Check the download logs for errors
- Verify the S3 sync completed successfully
""")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
