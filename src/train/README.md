# Hierarchical Loss Calculation

This document explains the logic for the parent loss calculation within the `forward` method of the `MarginalizationLoss` class.

### Code Block

```python
# --- 2. Parent Loss (for all samples) ---

# Predicted parent probabilities (shape: batch_size, num_internal_nodes)
# einsum('ij,kj->ki'): (internal, leaf) @ (batch, leaf) -> (batch, internal)
output_internal_prob = torch.einsum('ij,kj->ki', self.marginalization_tensor, outputs)
output_internal_prob = torch.clamp(output_internal_prob, 0, 1)

# True parent labels (shape: batch_size, num_internal_nodes)
true_parents_all = self.parent_child_tensor[y_batch]
target_internal_prob = true_parents_all[:, self.internal_indices]

# Exclusion mask (shape: batch_size, num_internal_nodes)
exclusion_mask_all = self.exclusion_tensor[y_batch]
exclusion_mask = exclusion_mask_all[:, self.internal_indices]

# Weighted BCE Loss for internal nodes
loss_parents = F.binary_cross_entropy(
    output_internal_prob, 
    target_internal_prob, 
    weight=exclusion_mask, 
    reduction='mean'
)
```

### Line-by-Line Explanation

1.  `output_internal_prob = torch.einsum(...)`
    *   **What:** This line calculates the **predicted** probability for each internal node by summing its descendant leaf probabilities.
    *   **How:** It performs an efficient matrix multiplication (`einsum`) between the `marginalization_tensor` (shape: `num_internal, num_leaf`) and the model's `outputs` (shape: `batch_size, num_leaf`).
    *   **Why:** The `'ij,kj->ki'` signature is a highly optimized way to perform this calculation and directly output a tensor of the desired shape: `(batch_size, num_internal_nodes)`.

2.  `output_internal_prob = torch.clamp(...)`
    *   **What:** A safety step to ensure all predicted probabilities are strictly between 0 and 1.
    *   **Why:** `BCELoss` will fail if any input is outside the `[0, 1]` range. This prevents errors from tiny floating-point inaccuracies.

3.  `true_parents_all = self.parent_child_tensor[y_batch]`
    *   **What:** This fetches the complete "true ancestor" vector for every sample in the batch.
    *   **How:** It uses the integer labels from `y_batch` to perform a single, high-speed indexing operation on the `parent_child_tensor` created during initialization.
    *   **Why:** This is the "best of both worlds" performance gain. The result, `true_parents_all`, is a tensor of shape `(batch_size, num_all_cells)`.

4.  `target_internal_prob = true_parents_all[:, self.internal_indices]`
    *   **What:** This filters the full ancestor vectors down to include **only the internal nodes**.
    *   **How:** It selects all rows (`:`) and only the columns specified in `self.internal_indices`.
    *   **Why:** The parent loss is only calculated over internal nodes, so we need the ground truth to match. The result, `target_internal_prob`, has the shape `(batch_size, num_internal_nodes)`, perfectly matching `output_internal_prob`.

5.  `exclusion_mask_all = self.exclusion_tensor[y_batch]`
    *   **What:** This fetches the correct exclusion mask for every sample in the batch.
    *   **How/Why:** It works exactly like the `true_parents_all` lookup, but on the `exclusion_tensor`. The result is a tensor of shape `(batch_size, num_all_cells)`.

6.  `exclusion_mask = exclusion_mask_all[:, self.internal_indices]`
    *   **What:** This filters the exclusion masks down to include **only the internal nodes**.
    *   **How/Why:** This ensures the `exclusion_mask` has the shape `(batch_size, num_internal_nodes)`, which is required for the next step.

7.  `loss_parents = F.binary_cross_entropy(...)`
    *   **What:** This is the final, correct calculation of the parent loss.
    *   **How:** It uses the functional version of BCE loss, passing our `exclusion_mask` to the `weight` parameter.
    *   **Why:** This tells PyTorch to multiply the loss for each element by its corresponding weight (`0` or `1`) in the mask before averaging. This elegantly achieves our goal of ignoring the loss for descendants of internal nodes.

---

### `F.binary_cross_entropy` Function Explained

The function signature we use is:
`F.binary_cross_entropy(input, target, weight, reduction='mean')`

Here are the arguments and how we use them:

1.  **`input`**: This is the tensor of predicted probabilities from the model.
    *   **Our value:** `output_internal_prob`
    *   **Requirement:** A tensor with values between 0 and 1.
    *   **Correctness:** **Yes.** Our tensor has the shape `(batch_size, num_internal_nodes)` and we use `torch.clamp` to ensure its values are in the `[0, 1]` range.

2.  **`target`**: This is the ground-truth tensor of true labels.
    *   **Our value:** `target_internal_prob`
    *   **Requirement:** A tensor with the same shape as `input`, containing only 0s and 1s.
    *   **Correctness:** **Yes.** Our tensor has the shape `(batch_size, num_internal_nodes)` and contains the true 0 or 1 labels for each internal node.

3.  **`weight`**: This is an optional tensor that acts as a multiplier for the loss of each individual element.
    *   **Our value:** `exclusion_mask`
    *   **Requirement:** A tensor with the same shape as `input`.
    *   **Correctness:** **Yes.** Our `exclusion_mask` has the shape `(batch_size, num_internal_nodes)`. Where the weight is `1`, the loss is counted normally. Where the weight is `0` (for the descendants of internal nodes), the loss for that element is multiplied by zero, effectively **ignoring it**. This is the correct and intended way to implement this masking logic.

4.  **`reduction`**: This specifies how to aggregate the final element-wise losses.
    *   **Our value:** `'mean'`
    *   **Requirement:** A string, typically `'mean'`, `'sum'`, or `'none'`.
    *   **Correctness:** **Yes.** Using `'mean'` correctly computes the average of all the weighted loss values, resulting in the single scalar number that we need for backpropagation.