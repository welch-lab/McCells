#!/bin/bash
#SBATCH --job-name=download_soma
#SBATCH --output=download_soma_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=24:00:00
#SBATCH --partition=sigbio

set -e

# Add the location of the AWS CLI to the PATH
# This is crucial for ensuring the command is found in an sbatch environment.
export PATH=$HOME/bin:$PATH

RELEASE_TAG="2025-01-30"
S3_URI="s3://cellxgene-census-public-us-west-2/cell-census/${RELEASE_TAG}/soma/census_data/homo_sapiens/"
OUTPUT_DIR="/scratch/sigbio_project_root/sigbio_project25/jingqiao/mccell-single/soma_db_homo_sapiens"

mkdir -p ${OUTPUT_DIR}

echo "Syncing Homo sapiens SOMA data for release ${RELEASE_TAG} from S3..."
echo "Source: ${S3_URI}"
echo "Destination: ${OUTPUT_DIR}"

aws s3 sync --no-sign-request ${S3_URI} ${OUTPUT_DIR}

echo "Download complete."