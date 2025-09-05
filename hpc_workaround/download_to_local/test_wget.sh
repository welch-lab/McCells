#!/bin/bash
# A simple script to test wget functionality.

echo "Testing wget..."

# Create a temporary directory for the download
TEMP_DIR=$(mktemp -d)
echo "Downloading to temporary directory: $TEMP_DIR"

# The URL to download
URL="https://cellxgene-census-public-us-west-2.s3.us-west-2.amazonaws.com/cell-census/2025-01-30/h5ads/eec804b9-2ae5-44f0-a1b5-d721e21257de.h5ad"

# Run wget
wget -P "$TEMP_DIR" "$URL"

# Check if the download was successful
if [ $? -eq 0 ]; then
    echo "wget test successful. File downloaded to $TEMP_DIR"
else
    echo "wget test failed."
fi
