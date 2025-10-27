# McCell Project Context

## Project Overview
McCell is a machine learning project for cell type classification using the CellXGene Census database. It focuses on hematopoietic cells (blood cells) and uses ontology-based hierarchical classification.

## Recent Changes (2025-10-24)

### 1. Fixed Cell Filter Bug in Data Loader
**Issue**: The dataloader was counting cells across the entire database before filtering, instead of counting only cells from 10x v3 primary experiments.

**Fix** (`src/data_pipeline/data_loader.py:33-38`):
- Now filters for `assay == "10x 3' v3" and is_primary_data == True` BEFORE counting cells
- Then applies the 5000 cell threshold to only those filtered cells
- Result: Found 80 cell types (down from 141) that actually have >5000 cells in 10x v3 primary experiments

### 2. Reorganized Data Structure
**New Structure**:
```
data/processed/
├── ontology.pkl (stays at root)
├── README.md (stays at root)
├── 10-17/ (old data with bug)
│   ├── 2025-10-17_marginalization_df.csv
│   ├── 2025-10-17_parent_child_df.csv
│   ├── 2025-10-17_exclusion_df.csv
│   ├── 2025-10-17_mapping_dict_df.csv
│   ├── 2025-10-17_leaf_values.pkl
│   └── 2025-10-17_internal_values.pkl
└── 10-24/ (new data with correct filter)
    ├── 2025-10-24_marginalization_df.csv
    ├── 2025-10-24_parent_child_df.csv
    ├── 2025-10-24_exclusion_df.csv
    ├── 2025-10-24_mapping_dict_df.csv
    ├── 2025-10-24_leaf_values.pkl
    └── 2025-10-24_internal_values.pkl
```

**Automation**: `run_preprocessing.py` now automatically creates dated folders (MM-DD format) when generating new data.

### 3. Created Utility Function for Path Management
**New function** (`src/utils/paths.py`):
```python
def get_data_folder(date: str) -> Path:
    """
    Get the path to the processed data folder for a given date.
    Args: date (str): 'YYYY-MM-DD' format (e.g., '2025-10-24')
    Returns: Path to data/processed/MM-DD/ folder
    """
```

**Updated scripts** to use this function:
- `hpc_workaround/draft_census_hvgs/compute_hvgs_cluster.py`
- `hpc_workaround/draft_census_hvgs/compute_hvgs.py`
- `hpc_workaround/draft_census_hvgs/select_genes_biomart.py`
- `train_blood_cell.ipynb`

All now use: `PROCESSED_DATA_DIR = get_data_folder(DATE)`

## Current Data Status
- **Active dataset**: 2025-10-24 (80 cell types, 23 leaf, 57 internal)
- **Root CL ID**: CL:0000988 (hematopoietic cell)
- **Filter criteria**: 10x 3' v3, primary data only, >5000 cells per type

## How to Run Preprocessing
```bash
uv run python run_preprocessing.py
```
This will:
1. Load ontology from cache
2. Query CellXGene Census with corrected filter
3. Generate all 6 preprocessed files
4. Automatically save to dated folder (e.g., `data/processed/10-24/`)

## Key Files
- `src/data_pipeline/data_loader.py` - Cell metadata loading with filters
- `src/data_pipeline/preprocess_ontology.py` - Ontology preprocessing
- `src/train/loss.py` - MarginalizationLoss implementation
- `src/train/model.py` - SimpleNN model
- `run_preprocessing.py` - Main preprocessing pipeline
- `train_blood_cell.ipynb` - Training notebook

## Important Notes
- Always use `get_data_folder(date)` when loading processed data
- Update `DATE` variable in scripts to switch between data versions
- The 10-24 dataset has the CORRECT filter (10x v3 primary only)
- The 10-17 dataset has the OLD BUGGY filter (all experiments)
