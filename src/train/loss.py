import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd


class MarginalizationLoss(nn.Module):
    """
    Calculates a hierarchical loss by combining a weighted leaf loss (for leaf-labeled data)
    and a parent loss (for all data).
    """
    def __init__(self, marginalization_df, parent_child_df, exclusion_df, 
                 leaf_values, internal_values, mapping_dict, leaf_weight=8.0, device='cpu'):
        super().__init__()
        self.leaf_weight = leaf_weight
        self.device = device

        # --- Store integer indices for slicing ---
        # The set of global indices that correspond to leaf nodes.
        self.leaf_indices_set = {mapping_dict[cid] for cid in leaf_values}
        
        # The CrossEntropyLoss for leaf node predictions.
        self.criterion_leafs = nn.CrossEntropyLoss(reduction='mean')

        # --- Parent loss components will be initialized in the next step ---

    def forward(self, outputs, y_batch):
        """The main forward pass for the loss function."""
        
        # --- 1. Leaf Loss (for leaf-labeled samples only) ---
        # Find samples in the batch that have a leaf node as their true label.
        is_leaf_mask = torch.tensor([y.item() in self.leaf_indices_set for y in y_batch], device=self.device)
        
        leaf_outputs = outputs[is_leaf_mask]
        leaf_y_batch = y_batch[is_leaf_mask]

        loss_leafs = torch.tensor(0.0, device=self.device)
        if leaf_outputs.shape[0] > 0:
            # Because of our ordered mapping_dict, the labels in leaf_y_batch are guaranteed
            # to be in the range [0, n_leaves-1], which matches the output dimensions.
            loss_leafs = self.criterion_leafs(leaf_outputs, leaf_y_batch) * self.leaf_weight

        # --- 2. Parent Loss (Placeholder) ---
        loss_parents = torch.tensor(0.0, device=self.device)
            
        # --- Total Loss ---
        total_loss = loss_leafs + loss_parents
        
        return total_loss, loss_leafs, loss_parents