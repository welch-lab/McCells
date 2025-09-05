import torch
import torch.nn as nn
from sklearn.preprocessing import LabelEncoder
import tiledbsoma
import tiledbsoma.ml as soma_ml
import os
import pandas as pd

# --- Configuration ---
# The URI of the SOMA Experiment created in the ingestion step
EXPERIMENT_URI = "/scratch/sigbio_project_root/sigbio_project25/jingqiao/mccell-single/soma_experiment"

# The path to your gene list file
MART_EXPORT_PATH = "/path/to/your/mart_export.txt" # IMPORTANT: Update this path

# The name of the measurement to use
MEASUREMENT_NAME = "RNA"

# The name of the obs column to use for labels
LABEL_COLUMN = "cell_type"

# An example filter to apply to the data
VALUE_FILTER = "n_genes > 1000"

def train_model():
    """
    Trains a simple PyTorch model on data from a SOMA Experiment,
    with filtering for protein-coding genes and calibrated shuffling.
    """
    if not os.path.exists(EXPERIMENT_URI):
        print(f"SOMA Experiment not found at {EXPERIMENT_URI}")
        print("Please run ingest_h5ad_to_soma.py first.")
        return

    # 1. Load the list of protein-coding genes
    print(f"Loading protein-coding genes from {MART_EXPORT_PATH}...")
    try:
        biomart = pd.read_csv(MART_EXPORT_PATH)
        coding_only = biomart[biomart['Gene type'] == 'protein_coding']
        gene_list = coding_only['Gene stable ID'].to_list()
        print(f"Found {len(gene_list)} protein-coding genes.")
    except FileNotFoundError:
        print(f"Error: {MART_EXPORT_PATH} not found. Please update the path.")
        return

    # 2. Open the SOMA Experiment and create a query with filters
    print(f"Opening SOMA Experiment and applying filters...")
    with tiledbsoma.open(EXPERIMENT_URI) as experiment:
        query = experiment.axis_query(
            measurement_name=MEASUREMENT_NAME,
            obs_query=tiledbsoma.AxisQuery(value_filter=VALUE_FILTER),
            var_query=tiledbsoma.AxisQuery(coords=(gene_list,))
        )

        # 3. Create the PyTorch ExperimentDataset with calibrated shuffling
        print("Creating PyTorch ExperimentDataset...")
        dataset = soma_ml.ExperimentDataset(
            query=query,
            layer_name="X",
            obs_column_names=[LABEL_COLUMN],
            batch_size=128,
            shuffle=True,
            shuffle_chunk_size=64,
            io_batch_size=65536
        )

        # 4. Create the PyTorch DataLoader
        print("Creating PyTorch DataLoader...")
        dataloader = torch.utils.data.DataLoader(
            dataset,
            num_workers=0
        )
        
        # 5. Encode labels for the filtered data
        print("Encoding labels for the filtered data...")
        all_labels = query.obs(column_names=[LABEL_COLUMN]).concat().to_pandas()[LABEL_COLUMN].to_numpy()
        le = LabelEncoder()
        le.fit(all_labels)
        n_classes = len(le.classes_)
        print(f"Found {n_classes} classes in the filtered data.")

        # 6. Define and train a simple PyTorch model
        print("\nStarting model training (example loop)...")
        # The number of features is now the number of genes in our list
        n_features = len(gene_list)
        model = nn.Linear(n_features, n_classes)
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

        for epoch in range(2):
            for i, batch in enumerate(dataloader):
                if i > 5:
                    break
                
                inputs = batch['X']
                labels_str = batch[LABEL_COLUMN]
                labels = torch.tensor(le.transform(labels_str))

                print(f"[Epoch {epoch + 1}, Batch {i + 1}] Input shape: {inputs.shape}, Labels shape: {labels.shape}")

        print("\nFinished example training loop.")

if __name__ == "__main__":
    train_model()
