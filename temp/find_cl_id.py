import pronto
import os

# This will download 'cl.owl' from the OBO library if not found locally.
# It assumes the script is run from a location where it can write to the current directory
# or that cl.owl is already present.
print("Loading Cell Ontology (will download if necessary)...")
try:
    cl_ontology = pronto.Ontology.from_obo_library('cl.owl')
    print("Ontology loaded successfully.")
except Exception as e:
    print(f"Failed to load ontology: {e}")
    exit(1)

hematopoietic_cell_id = None
for term in cl_ontology.terms():
    if term.name == "hematopoietic cell":
        hematopoietic_cell_id = term.id
        break

if hematopoietic_cell_id:
    print(f"CL ID for 'hematopoietic cell': {hematopoietic_cell_id}")
else:
    print("'hematopoietic cell' not found in ontology.")
