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
    M[child_idx][parent_idx] = 1 if parent is not subclass of child, else 0
    """
    num_parents = len(all_cell_values)
    num_children = len(all_cell_values)
    mask = torch.ones(num_children, num_parents)

    type_to_idx = {p: i for i, p in enumerate(all_cell_values)}

    for cell in all_cell_values:
        try:
            children = cl[cell].subclasses(with_self=True)
            for subclass in children:
                if subclass.id in type_to_idx:
                    mask[type_to_idx[cell], type_to_idx[subclass.id]] = 0
        except KeyError:
            continue

    return mask


def preprocess_data_ontology(cl, labels, target_column, upper_limit=None, cl_only=False, include_leafs=False):
    """
    This function performs preprocessing on an AnnData object to prepare it for modelling.
    Only the input labels are included in the mask and mapping dicts.
    """
    all_cell_values = labels[target_column].astype('category').unique().tolist()
    mapping_dict = {term_id: i for i, term_id in enumerate(all_cell_values)}
    leaf_values = [term_id for term_id in all_cell_values if cl[term_id].is_leaf()]
    internal_values = [term_id for term_id in all_cell_values if not cl[term_id].is_leaf()]

    labels['encoded_labels'] = labels[target_column].map(mapping_dict)

    # Square ontology_df and mask for only the input labels
    ontology_df = build_ontology_df(all_cell_values, all_cell_values, cl)
    cell_parent_mask = build_parent_child_mask(all_cell_values, all_cell_values, cl, include_self=True)

    return mapping_dict, leaf_values, internal_values, ontology_df, cell_parent_mask
