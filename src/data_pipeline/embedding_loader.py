"""Data loader for precomputed ESM-2 cell embeddings.

Loads cell embeddings (.npy) and metadata (.csv) produced by the
protein-cell-embed pipeline (Stage 1) for use in McCell training.
"""

import logging
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

logger = logging.getLogger(__name__)


class CellEmbeddingDataset(Dataset):
    """PyTorch Dataset for precomputed cell embeddings + cell type labels.

    Args:
        embeddings: (n_cells, embedding_dim) numpy array of cell embeddings.
        labels: (n_cells,) numpy array of integer-encoded cell type labels.
    """

    def __init__(self, embeddings: np.ndarray, labels: np.ndarray):
        assert len(embeddings) == len(labels), (
            f"Mismatch: {len(embeddings)} embeddings vs {len(labels)} labels"
        )
        self.embeddings = torch.tensor(embeddings, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.embeddings[idx], self.labels[idx]


def load_cell_embeddings(
    embeddings_path: Path,
    metadata_path: Path,
    label_column: str = "cell_type_ontology_term_id",
    mapping_dict: dict = None,
) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """Load precomputed cell embeddings and align with cell type labels.

    Args:
        embeddings_path: Path to .npy file with cell embeddings.
        metadata_path: Path to .csv file with cell metadata.
        label_column: Column name containing cell type ontology term IDs.
        mapping_dict: Dict mapping CL IDs to integer indices (from preprocess_ontology).
            If None, returns raw string labels.

    Returns:
        Tuple of (embeddings, encoded_labels, metadata_df).
    """
    logger.info(f"Loading cell embeddings from {embeddings_path}")
    embeddings = np.load(embeddings_path)
    logger.info(f"  Shape: {embeddings.shape}")

    logger.info(f"Loading metadata from {metadata_path}")
    metadata = pd.read_csv(metadata_path, index_col=0)
    logger.info(f"  Rows: {len(metadata)}")

    assert len(embeddings) == len(metadata), (
        f"Mismatch: {len(embeddings)} embeddings vs {len(metadata)} metadata rows"
    )

    if mapping_dict is not None:
        # Encode labels using the ontology mapping
        valid_mask = metadata[label_column].isin(mapping_dict)
        n_valid = valid_mask.sum()
        logger.info(
            f"  {n_valid}/{len(metadata)} cells have labels in mapping_dict "
            f"({n_valid / len(metadata) * 100:.1f}%)"
        )

        # Filter to cells with valid labels
        embeddings = embeddings[valid_mask.values]
        metadata = metadata[valid_mask]
        encoded_labels = metadata[label_column].map(mapping_dict).values.astype(np.int64)
    else:
        encoded_labels = metadata[label_column].values

    return embeddings, encoded_labels, metadata


def create_embedding_dataloaders(
    embeddings: np.ndarray,
    labels: np.ndarray,
    train_frac: float = 0.8,
    val_frac: float = 0.1,
    batch_size: int = 256,
    seed: int = 42,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Create train/val/test DataLoaders from embeddings and labels.

    Args:
        embeddings: (n_cells, embedding_dim) array.
        labels: (n_cells,) integer-encoded labels.
        train_frac: Fraction of data for training.
        val_frac: Fraction of data for validation. Test = 1 - train - val.
        batch_size: Batch size for DataLoaders.
        seed: Random seed for reproducible splits.

    Returns:
        Tuple of (train_loader, val_loader, test_loader).
    """
    n = len(labels)
    rng = np.random.RandomState(seed)
    indices = rng.permutation(n)

    n_train = int(n * train_frac)
    n_val = int(n * val_frac)

    train_idx = indices[:n_train]
    val_idx = indices[n_train:n_train + n_val]
    test_idx = indices[n_train + n_val:]

    logger.info(f"Data split: train={len(train_idx)}, val={len(val_idx)}, test={len(test_idx)}")

    train_ds = CellEmbeddingDataset(embeddings[train_idx], labels[train_idx])
    val_ds = CellEmbeddingDataset(embeddings[val_idx], labels[val_idx])
    test_ds = CellEmbeddingDataset(embeddings[test_idx], labels[test_idx])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    return train_loader, val_loader, test_loader
