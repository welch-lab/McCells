# Processed Ontology Data

This directory contains the processed ontology data derived from the Cell Ontology (CL).

## Files

### `ontology.parquet`

This file contains the main ontology hierarchy represented as a DataFrame. The structure is as follows:

- **Index**: Parent CL terms (e.g., "CL:0000000").
- **Columns**: All CL terms present in the ontology.
- **Values**: An integer `1` indicates that the term in the index is an ancestor of the term in the column. Otherwise, the value is `0`.

This file can be used to look up all descendants of a given ontology term.

### `ontology_metadata.parquet`

This file contains metadata for each term in the ontology.

- **cl_id**: The official Cell Ontology ID (e.g., "CL:0000000"). This is the index of the dataframe.
- **cl_name**: The human-readable name for the ontology term (e.g., "cell").
- **cl_idx**: A signed integer index used to distinguish leaf nodes from internal nodes in the ontology graph. 
  - A **positive** value indicates that the term is a **leaf node** (it has no children).
  - A **negative** value indicates that the term is an **internal node** (it has children).
