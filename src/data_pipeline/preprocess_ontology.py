import pandas as pd
import torch
import pronto
from src.utils.paths import PROJECT_ROOT


def create_mapping_dicts(all_cell_values, cl):
    mapping_dict = {term_id: i for i, term_id in enumerate(all_cell_values)}
    leaf_values = []
    internal_values = []
    for term_id in all_cell_values:
        if cl[term_id].is_leaf():
            leaf_values.append(term_id)
        else:
            internal_values.append(term_id)
    return mapping_dict, leaf_values, internal_values


def get_parent_nodes(all_cell_values, cl, upper_limit=None, cl_only=False, include_leafs=False):
    all_parent_nodes = []
    for target in all_cell_values:
        try:
            for term in cl[target].superclasses(with_self=include_leafs):
                all_parent_nodes.append(term.id)
        except KeyError:
            continue

    all_parent_nodes = sorted(list(set(all_parent_nodes)))

    if cl_only:
        all_parent_nodes = [x for x in all_parent_nodes if x.startswith('CL')]

    if upper_limit is not None:
        try:
            upper_limit_nodes = [term.id for term in cl[upper_limit].superclasses(with_self=False)]
            all_parent_nodes = [x for x in all_parent_nodes if x not in upper_limit_nodes]
        except KeyError:
            pass

    return all_parent_nodes


def build_ontology_df(all_parent_nodes, all_cell_values, cl):
    ontology_df = pd.DataFrame(data=0, index=all_parent_nodes, columns=all_cell_values)
    for cell_id in ontology_df.index:
        try:
            for term in cl[cell_id].subclasses(with_self=True):
                if term.id in ontology_df.columns:
                    ontology_df.loc[cell_id, [term.id]] = 1
        except KeyError:
            continue
    return ontology_df


def build_parent_child_mask(all_cell_values, all_parent_nodes, cl, include_self=False):
    """
    M[parent_idx][child_idx] = 0 if parent is ancestor of child, else 1
    """
    num_parents = len(all_parent_nodes)
    num_children = len(all_cell_values)
    mask = torch.ones(num_parents, num_children)

    parent_to_idx = {p: i for i, p in enumerate(all_parent_nodes)}
    child_to_idx = {c: j for j, c in enumerate(all_cell_values)}

    for child in all_cell_values:
        try:
            ancestors = cl[child].superclasses(with_self=include_self)
            for term in ancestors:
                if term.id in parent_to_idx:
                    mask[parent_to_idx[term.id], child_to_idx[child]] = 0
        except KeyError:
            continue

    return mask


def preprocess_data_ontology(cl, labels, target_column, upper_limit=None, cl_only=False, include_leafs=False):
    all_cell_values = labels[target_column].astype('category').unique().tolist()

    mapping_dict, leaf_values, internal_values = create_mapping_dicts(all_cell_values, cl)
    labels['encoded_labels'] = labels[target_column].map(mapping_dict)

    all_parent_nodes = get_parent_nodes(all_cell_values, cl, upper_limit, cl_only, include_leafs)
    ontology_df = build_ontology_df(all_parent_nodes, all_cell_values, cl)

    # ✅ New correct masking function
    cell_parent_mask = build_parent_child_mask(all_cell_values, all_parent_nodes, cl, include_self=True)

    return mapping_dict, leaf_values, internal_values, ontology_df, cell_parent_mask
