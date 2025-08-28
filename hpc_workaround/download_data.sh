#!/bin/bash

# This script downloads the H5AD files listed in h5ad_links.txt using wget.

# Get the directory of the current script
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
LINKS_FILE="$SCRIPT_DIR/h5ad_links.txt"

if [ ! -f "$LINKS_FILE" ]; then
    echo "Error: $LINKS_FILE not found. Please run get_h5ad_links.py first."
    exit 1
fi

echo "Starting download..."
wget --input-file="$LINKS_FILE" --continue --directory-prefix=/nfs/turbo/umms-welchjd/Mccells-data

echo "Download complete."
