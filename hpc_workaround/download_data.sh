#!/bin/bash
#SBATCH --job-name=wget_download
#SBATCH --output=wget_download_%j.out
#SBATCH --error=wget_download_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=1:00:00

# This script downloads the H5AD files listed in h5ad_links.txt using wget.

# Get the directory of the current script
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
LINKS_FILE="$SCRIPT_DIR/h5ad_links.txt"

if [ ! -f "$LINKS_FILE" ]; then
    echo "Error: $LINKS_FILE not found. Please run get_h5ad_links.py first."
    exit 1
fi

echo "Converting S3 URIs to HTTPS URLs and starting download..."
# Create a temporary file for the https links
HTTPS_LINKS_FILE=$(mktemp)
sed 's|s3://cellxgene-census-public-us-west-2/|https://cellxgene-census-public-us-west-2.s3.us-west-2.amazonaws.com/|' "$LINKS_FILE" > "$HTTPS_LINKS_FILE"

wget --input-file="$HTTPS_LINKS_FILE" --continue --directory-prefix=/nfs/turbo/umms-welchjd/Mccells-data

# Clean up the temporary file
rm "$HTTPS_LINKS_FILE"

echo "Download complete."
