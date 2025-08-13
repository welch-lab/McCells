
import pandas as pd

try:
    df = pd.read_parquet('data/processed/ontology.parquet')
    print(df.head().to_markdown(index=False))
    print("\n--- DataFrame Info ---")
    df.info()
except Exception as e:
    print(f"Error reading parquet file: {e}")

