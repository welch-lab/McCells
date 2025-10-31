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

## Recent Changes (2025-10-31)

### 4. Fixed Gradient Explosion Issues (Commit cf62d35)

**Problem**: Training on HPC completed but loss exploded from ~20 to 130,000+ at batch 98,306 despite gradient clipping.

**Root Causes Identified**:
1. **Numerical instability**: `clamp(0, 1)` allowed `log(0) = -inf` in BCE loss
2. **Parameter drift**: With lr=1e-3 and 98k+ updates, weights drifted to extreme values
3. **Learning rate too high**: 1e-3 is 2x higher than old reference (SGD 5e-4)

**Fixes Applied** (`src/train/loss.py:77`, `train_blood_cell.ipynb` cell-5, cell-6):
1. Changed clamping: `torch.clamp(output_internal_prob, 1e-7, 1-1e-7)` prevents log(0)
2. Lowered learning rate: 1e-3 → 3e-4 (conservative for Adam)
3. Added Weights & Biases logging to monitor gradients and weights in real-time
4. Added gradient norm tracking (returned from `clip_grad_norm_`)

### 5. Discovered SOMA set_epoch() Bug

**Critical Finding**: SOMA's `set_epoch()` function **does not work** as documented!

**What it should do**: Combine seed with epoch to get different shuffles each epoch (like PyTorch's DistributedSampler)

**What it actually does**: Only sets `self.epoch = epoch` but **never uses it** in shuffle calculations

**Impact**: With `seed=111`, you get identical batches every epoch regardless of `set_epoch()` calls

**Decision**: Keep `seed=111` for reproducibility, don't call `set_epoch()` since it does nothing. Identical shuffle per epoch is standard practice and not a problem.

### 6. Understanding SOMA Shuffle Behavior

**Two-Stage Shuffle Process**:

1. **Chunk-level shuffle** (shuffle_chunk_size=64, default):
   - Divides cells into chunks of 64 contiguous cells
   - Shuffles chunk ORDER randomly
   - Groups shuffled chunks into IO batches (65,536 cells each)

2. **Cell-level shuffle** (within each IO batch):
   - Applies `np.random.permuted()` to individual cells
   - Creates 256-cell mini-batches from shuffled cells

**Potential Cell Type Clustering Issue**:
- If CellXGene stores cells clustered by type (e.g., cells 1-10k all monocytes)
- Chunks 1-156 would all be monocyte chunks
- Even after shuffling, IO batches might be homogeneous
- Would need to verify with `check_batch_diversity.py` on HPC (Census web API times out)

## Current Training Status

**Branch**: `filter-fix` (commit cf62d35)

**Ready for HPC Training** with these parameters:
- Learning rate: 3e-4 (Adam optimizer)
- Gradient clipping: max_norm=1.0
- Batch size: 256 cells per batch
- Shuffle: seed=111 (reproducible, same shuffle every epoch)
- Loss: Epsilon clamping prevents numerical instability
- Monitoring: Weights & Biases tracks gradients, loss, weights

**Training Configuration**:
- 6.3M cells → 24,936 batches after 80% train split → 19,665 batches per epoch
- 5 epochs = 98,325 total batches
- Model: SimpleNN (23,262 genes → 2048 → 1024 → 256 → 23 leaf nodes)
- Loss: MarginalizationLoss (leaf CrossEntropy + parent BCE with hierarchy)

## Important Notes
- Always use `get_data_folder(date)` when loading processed data
- Update `DATE` variable in scripts to switch between data versions
- The 10-24 dataset has the CORRECT filter (10x v3 primary only)
- The 10-17 dataset has the OLD BUGGY filter (all experiments)
- **NEVER use SOMA's `set_epoch()` - it's broken and does nothing**
- Cells ARE shuffled at individual level despite clustering concerns
