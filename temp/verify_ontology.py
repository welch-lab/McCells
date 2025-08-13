import pandas as pd

file_path = 'data/processed/ontology.parquet'

print(f'Attempting to read {file_path}...')

try:
    df = pd.read_parquet(file_path)
    print('File read successfully!')
    print('\n--- DataFrame Info ---')
    print(f'Shape: {df.shape}')
    print('\n--- First 5x5 Rows & Columns ---')
    print(df.iloc[:5, :5])
    print('\n--- Verification Complete ---')
except Exception as e:
    print(f'An error occurred: {e}')
