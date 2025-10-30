#!/bin/bash
#SBATCH --job-name=verify_soma
#SBATCH --output=verify_soma_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=2:00:00
#SBATCH --partition=standard

set -e

echo "=========================================="
echo "SOMA Database Verification Job"
echo "=========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $HOSTNAME"
echo "Started: $(date)"
echo ""

# Load necessary modules (adjust based on your environment setup)
# module load python/3.9  # Uncomment and adjust if needed

# Activate your conda/virtual environment if needed
# source activate your_env_name  # Uncomment and adjust if needed

# Run the verification script
python /scratch/sigbio_project_root/sigbio_project25/jingqiao/mccell-single/verify_soma_cell_counts.py

echo ""
echo "=========================================="
echo "Job completed: $(date)"
echo "=========================================="
