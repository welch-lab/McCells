import pandas as pd
import torch
import pronto
from src.utils.paths import PROJECT_ROOT

INTERNAL_NODE_ENCODING_START = -9999

def set_internal_node_values(cl, internal_values, all_parent_nodes):
    """
    Creates a dictionary where each key is an internal cell type and the values are the cell types
    we want to include when calculating the loss. We do not want to consider direct descendents of the
    internal cell type, so those are removed.
    """
    parent_dict = {}
    for internal_node in internal_values:
        child_nodes = [term.id for term in cl[internal_node].subclasses(with_self=True)]
        cell_types_to_include = [x for x in all_parent_nodes if x not in child_nodes]
        parent_dict[internal_node] = cell_types_to_include
    return parent_dict

def build_parent_mask(leaf_values, internal_values, ontology_df, parent_dict):
    """
    Builds a masking matrix for use when calculating the internal loss.
    """
    num_leafs = len(leaf_values)
    num_parents = ontology_df.shape[0]
    cell_parents_mask = torch.ones(num_parents, num_leafs)
    list_of_parents = ontology_df.index.tolist()

    for cell_id in internal_values:
        parent_list_for_cell = parent_dict[cell_id]
        parent_binary_list = [1 if parent in parent_list_for_cell else 0 for parent in list_of_parents]
        parent_binary_tensor = torch.tensor(parent_binary_list).reshape(-1, 1)
        cell_parents_mask = torch.cat((cell_parents_mask, parent_binary_tensor), 1)

    return cell_parents_mask

def preprocess_data_ontology(cl, labels, target_column, upper_limit=None, cl_only=False, include_leafs=False):
    """
    This function performs preprocessing on an AnnData object to prepare it for modelling.
    """
    all_cell_values = labels[target_column].astype('category').unique().tolist()

    mapping_dict = {}
    leaf_values = []
    internal_values = []
    encoded_leaf_val = 0
    encoded_internal_val = INTERNAL_NODE_ENCODING_START

    for term_id in all_cell_values:
        try:
            term = cl[term_id]
            if term.is_leaf():
                mapping_dict[term.id] = encoded_leaf_val
                leaf_values.append(term.id)
                encoded_leaf_val += 1
            else:
                mapping_dict[term.id] = encoded_internal_val
                internal_values.append(term.id)
                encoded_internal_val += 1
        except KeyError:
            print(f"Warning: Term ID {term_id} not found in ontology. Skipping.")
            continue

    labels['encoded_labels'] = labels[target_column].map(mapping_dict)

    all_parent_nodes = []
    for target in all_cell_values:
        try:
            for term in cl[target].superclasses(with_self=include_leafs):
                all_parent_nodes.append(term.id)
        except KeyError:
            continue

    all_parent_nodes = list(set(all_parent_nodes))

    if cl_only:
        all_parent_nodes = [x for x in all_parent_nodes if x.startswith('CL')]

    if upper_limit is not None:
        try:
            upper_limit_nodes = [term.id for term in cl[upper_limit].superclasses(with_self=False)]
            all_parent_nodes = [x for x in all_parent_nodes if x not in upper_limit_nodes]
        except KeyError:
            pass

    parent_dict = set_internal_node_values(cl, internal_values, all_parent_nodes)

    ontology_df = pd.DataFrame(data=0, index=all_parent_nodes, columns=all_cell_values)

    for cell_id in ontology_df.index:
        try:
            for term in cl[cell_id].subclasses(with_self=True):
                if term.id in ontology_df.columns:
                    ontology_df.loc[cell_id, [term.id]] = 1
        except KeyError:
            continue

    cell_parent_mask = build_parent_mask(leaf_values, internal_values, ontology_df, parent_dict)

    return mapping_dict, leaf_values, internal_values, ontology_df, parent_dict, cell_parent_mask