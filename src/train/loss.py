import torch
import torch.nn as nn
import pandas as pd

# --- Helper Functions for Parent Loss ---

def output_probability_tensor(outputs, ontology_leaf_df, device):
    """
    Calculates predicted parent probabilities by summing leaf probabilities up the ontology tree.

    The `einsum` operation 'ij,kj->ik' performs a batch matrix multiplication.
    - The ontology_tensor ('ij') is (num_parents, num_leaves).
    - The outputs tensor ('kj') is (batch_size, num_leaves).
    - The result ('ik') is (num_parents, batch_size), where each entry [i, k] is the
      sum of probabilities of all leaf descendants of parent i for cell k.
    """
    ontology_tensor = torch.FloatTensor(ontology_leaf_df.values).to(device)
    
    # Einsum for batch matrix multiplication: convolve parent-leaf relationships with leaf probabilities
    # i = parent, j = leaf, k = cell in batch
    probability_tensor = torch.einsum('ij,kj->ik', ontology_tensor, outputs)
    
    # Clamp values to be max 1.0 to avoid floating point errors with BCE loss
    probability_tensor = torch.where(probability_tensor > 1, 1.0, probability_tensor)

    return probability_tensor

def target_probability_tensor(target_values, ontology_df, mapping_dict, device):
    """
    Creates the true multi-label vectors for the parent nodes based on the ground truth.
    """
    inv_mapping_dict = {v: k for k, v in mapping_dict.items()}
    
    target_tensor_list = []
    for target_value in target_values:
        target_cell_id = inv_mapping_dict[target_value.item()]
        # For each true label, get its column from ontology_df, which lists all its ancestors
        sub_target_tensor = torch.tensor(ontology_df.loc[:, target_cell_id].values, dtype=torch.float).reshape(-1, 1)
        target_tensor_list.append(sub_target_tensor)
        
    target_tensor = torch.cat(target_tensor_list, dim=1).to(device)
    return target_tensor

# --- Loss Component Functions ---

def compute_leaf_loss(outputs, y_batch, criterion, leaf_weight, device):
    """Calculates the weighted cross-entropy loss for leaf nodes."""
    loss = criterion(outputs, y_batch)
    loss = loss * leaf_weight
    if torch.isnan(loss):
        loss = torch.tensor(0.0, device=device)
    return loss

def compute_parent_loss(outputs, y_batch, ontology_df, ontology_leaf_df, mapping_dict, criterion, device):
    """Calculates the BCE loss for parent nodes."""
    output_parent_prob = output_probability_tensor(outputs, ontology_leaf_df, device)
    target_parent_prob = target_probability_tensor(y_batch, ontology_df, mapping_dict, device)
    loss = criterion(output_parent_prob, target_parent_prob)
    return loss

# --- Main Loss Class ---

class MarginalizationLoss(nn.Module):
    """
    Calculates a hierarchical loss by combining a weighted leaf loss and a parent loss.
    """
    def __init__(self, ontology_df, leaf_values, mapping_dict, leaf_weight=8.0, device='cpu'):
        super().__init__()
        self.leaf_weight = leaf_weight
        self.device = device
        
        # Store data required for loss calculations
        self.ontology_df = ontology_df
        self.ontology_leaf_df = ontology_df[leaf_values].copy()
        self.mapping_dict = mapping_dict
        
        # Define the criterion for each loss component
        self.criterion_leafs = nn.CrossEntropyLoss(reduction='mean')
        self.criterion_parents = nn.BCELoss(reduction='mean')

    def forward(self, outputs, y_batch):
        """The main forward pass for the loss function."""
        
        # --- 1. Leaf Loss ---
        loss_leafs = compute_leaf_loss(
            outputs, y_batch, self.criterion_leafs, self.leaf_weight, self.device
        )
        
        # --- 2. Parent Loss ---
        loss_parents = compute_parent_loss(
            outputs, y_batch, self.ontology_df, self.ontology_leaf_df, 
            self.mapping_dict, self.criterion_parents, self.device
        )
            
        # --- Total Loss ---
        total_loss = loss_leafs + loss_parents
        
        return total_loss, loss_leafs, loss_parents
