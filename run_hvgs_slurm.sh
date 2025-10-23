#!/bin/bash
#SBATCH --job-name=compute_hvgs
#SBATCH --time=00:30:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=4
#SBATCH --output=hvgs_computation_%j.log
#SBATCH --error=hvgs_computation_%j.err

# Print job info
echo "======================================"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $HOSTNAME"
echo "Started: $(date)"
echo "======================================"
echo ""

# Load modules if needed (adjust for your cluster)
# module load python/3.11  # Uncomment if needed

# Navigate to project directory
cd ~/real_McCell

# Ensure dependencies are synced with uv
echo "Syncing dependencies with uv..."
uv sync

# Test internet connectivity
echo "Testing internet connectivity..."
curl -Is https://cellxgene-census-public-us-west-2.s3.us-west-2.amazonaws.com | head -1

# Run the HVG computation
echo ""
echo "Starting HVG computation..."
uv run compute_hvgs_cluster.py

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "SUCCESS! HVGs computed."
    echo "Finished: $(date)"
    echo "======================================"
else
    echo ""
    echo "======================================"
    echo "FAILED! Check errors above."
    echo "Finished: $(date)"
    echo "======================================"
    exit 1
fi
