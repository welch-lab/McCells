import unittest
import torch
import pandas as pd
import sys
import os

# Add the project root to the Python path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.train.loss import output_probability_tensor, target_probability_tensor

class TestLossFunctions(unittest.TestCase):

    def setUp(self):
        """Set up a toy example for all tests."""
        self.device = 'cpu'

        # 1. Define a mini-ontology
        parents = ['parent_AB', 'parent_C', 'root']
        leaves = ['leaf_A', 'leaf_B', 'leaf_C']
        
        # The ontology_df has parents as rows and leaves as columns.
        # A 1 indicates that the parent is an ancestor of the leaf.
        ontology_data = {
            'leaf_A': [1, 0, 1], # Ancestors: parent_AB, root
            'leaf_B': [1, 0, 1], # Ancestors: parent_AB, root
            'leaf_C': [0, 1, 1], # Ancestors: parent_C, root
        }
        self.ontology_df = pd.DataFrame(ontology_data, index=parents)
        self.ontology_leaf_df = self.ontology_df # In this simple case, they are the same

        self.mapping_dict = {name: i for i, name in enumerate(leaves)}

        # 2. Create dummy model predictions for a batch of 2 cells
        self.outputs = torch.tensor([
            [0.8, 0.1, 0.1],  # Cell 0: Model is 80% sure it's leaf_A
            [0.1, 0.2, 0.7]   # Cell 1: Model is 70% sure it's leaf_C
        ], device=self.device)

        # 3. Create dummy ground truth labels for the 2 cells
        self.y_batch = torch.tensor([
            self.mapping_dict['leaf_A'], # Cell 0 is actually leaf_A
            self.mapping_dict['leaf_C']  # Cell 1 is actually leaf_C
        ], device=self.device)

    def test_output_probability_tensor(self):
        """
        Tests that predicted parent probabilities are calculated correctly.
        """
        predicted_parent_probs = output_probability_tensor(
            self.outputs, self.ontology_leaf_df, self.device
        )
        
        # Expected result shape: (num_parents, num_cells)
        expected_probs = torch.tensor([
            # Cell 0: P(A)+P(B)=0.9, Cell 1: P(A)+P(B)=0.3
            [0.9, 0.3], 
            # Cell 0: P(C)=0.1,       Cell 1: P(C)=0.7
            [0.1, 0.7], 
            # Cell 0: P(A)+P(B)+P(C)=1.0, Cell 1: P(A)+P(B)+P(C)=1.0
            [1.0, 1.0]  
        ], device=self.device)
        
        self.assertTrue(torch.allclose(predicted_parent_probs, expected_probs))

    def test_target_probability_tensor(self):
        """
        Tests that the true parent multi-label vectors are created correctly.
        """
        true_parent_labels = target_probability_tensor(
            self.y_batch, self.ontology_df, self.mapping_dict, self.device
        )
        
        # Expected result shape: (num_parents, num_cells)
        expected_labels = torch.tensor([
            # Cell 0 (is leaf_A): Ancestors are parent_AB, root
            # Cell 1 (is leaf_C): Ancestors are parent_C, root
            [1, 0],
            [0, 1],
            [1, 1]
        ], device=self.device, dtype=torch.float)

        self.assertTrue(torch.allclose(true_parent_labels, expected_labels))

    def test_dag_no_double_counting_complex(self):
        """
        Tests that leaf probabilities are not double-counted in a more complex DAG.
        """
        # Hierarchy: C->pCD, D->pCD, D->pDE, E->pDE. root is parent of all.
        #          root
        #         /    \
        #       pCD    pDE
        #      /   \  /   \
        #     C     D      E
        parents = ['pCD', 'pDE', 'root']
        leaves = ['C', 'D', 'E']
        
        # ontology_leaf_df[parent, leaf] = 1 if parent is ancestor
        ontology_data = {
            'C': [1, 0, 1], # Ancestors: pCD, root
            'D': [1, 1, 1], # Ancestors: pCD, pDE, root
            'E': [0, 1, 1]  # Ancestors: pDE, root
        }
        ontology_leaf_df = pd.DataFrame(ontology_data, index=parents)

        # Model predicts probabilities for a single cell
        outputs = torch.tensor([[0.6, 0.3, 0.1]], device=self.device) # P(C), P(D), P(E)

        # --- Act ---
        predicted_parent_probs = output_probability_tensor(
            outputs, ontology_leaf_df, self.device
        )

        # --- Assert ---
        # P(pCD) = P(C) + P(D) = 0.6 + 0.3 = 0.9
        # P(pDE) = P(D) + P(E) = 0.3 + 0.1 = 0.4
        # P(root) = P(C) + P(D) + P(E) = 0.6 + 0.3 + 0.1 = 1.0
        # A naive recursive sum P(root) = P(pCD) + P(pDE) would double-count P(D) and give 1.3.
        expected_probs = torch.tensor([
            [0.9],
            [0.4],
            [1.0]
        ], device=self.device)

        self.assertTrue(torch.allclose(predicted_parent_probs, expected_probs))

    def test_internal_node_leaf_loss_is_zero(self):
        """
        Tests that leaf loss is zero when the true label is an internal node.
        """
        from src.train.loss import MarginalizationLoss

        # 1. Define a hierarchy with an internal node
        parents = ['parent_A', 'root']
        leaves = ['leaf_A']
        all_nodes = parents + leaves
        
        ontology_data = {
            'leaf_A':   [1, 1, 1],
            'parent_A': [1, 1, 0],
            'root':     [0, 1, 0],
        }
        ontology_df = pd.DataFrame(ontology_data, index=all_nodes)
        ontology_df = ontology_df[all_nodes]

        leaf_values = ['leaf_A']
        # mapping_dict now includes an internal node
        mapping_dict = {'leaf_A': 0, 'parent_A': 1, 'root': 2}

        # 2. Instantiate the loss function
        loss_fn = MarginalizationLoss(
            ontology_df=ontology_df,
            leaf_values=leaf_values,
            mapping_dict=mapping_dict,
            device=self.device
        )

        # 3. Create a batch where the true label is an internal node ('parent_A')
        y_batch = torch.tensor([1], device=self.device) # Index for 'parent_A'
        
        # Model predicts something for the leaf nodes
        outputs = torch.tensor([[0.9]], device=self.device) # P(leaf_A)

        # 4. Act: Calculate the loss
        total_loss, loss_leafs, loss_parents = loss_fn(outputs, y_batch)

        # 5. Assert
        self.assertEqual(loss_leafs.item(), 0.0)
        self.assertGreater(loss_parents.item(), 0.0)
        self.assertEqual(total_loss.item(), loss_parents.item())

if __name__ == '__main__':
    unittest.main()
