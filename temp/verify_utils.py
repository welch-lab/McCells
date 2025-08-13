from src.utils.ontology_utils import load_ontology, get_sub_DAG, get_cell_info

def main():
    cl = load_ontology()
    if cl is None:
        return

    print("--- Testing get_sub_DAG ---")
    descendants = get_sub_DAG(cl, 'CL:0000988')
    print(f"Found {len(descendants)} descendants for CL:0000988.")
    print('CL:0000988' in descendants) # Should be True
    print('CL:0000236' in descendants) # B cell, should be True
    print('CL:0000151' in descendants) # adrenal cell, should be False


    print("\n--- Testing get_cell_info ---")
    info = get_cell_info(cl, ['CL:0000988', 'CL:0000000'])
    print(info)

if __name__ == "__main__":
    main()
