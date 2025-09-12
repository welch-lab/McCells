#!/bin/bash
#SBATCH --job-name=wget_download
#SBATCH --output=wget_download_%j.out
#SBATCH --error=wget_download_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=1:00:00
#SBATCH --partition=sigbio


RELEASE_TAG="2025-01-30"
BASE_URL="https://cellxgene-census-public-us-west-2.s3.us-west-2.amazonaws.com"
DATA_PATH="cell-census/${RELEASE_TAG}/soma"
OUTPUT_DIR="/scratch/sigbio_project_root/sigbio_project25/jingqiao/mccell-single/soma_db"

echo "Downloading SOMA data for release ${RELEASE_TAG}..."
echo "Output directory: ${OUTPUT_DIR}"

# -r: recursive
# -np: no-parent (don't go to parent directories)
# -nH: no-host-directories (don't create a directory named after the host)
# --cut-dirs=3: remove the first 3 directories from the path (cell-census, ${RELEASE_TAG}, soma)
# -R "index.html*": reject index.html files
# --directory-prefix: download files into this directory
wget -r -np -nH --cut-dirs=3 -R "index.html*" --directory-prefix=${OUTPUT_DIR} ${BASE_URL}/${DATA_PATH}/

echo "Download complete."