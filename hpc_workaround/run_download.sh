#!/bin/bash
#
# This is a Slurm batch script to run your Python data download and processing.
#
#SBATCH --job-name=census_download      # A name for your job (appears in squeue)
#SBATCH --output=census_download_%j.out # Standard output file (%j is replaced by job ID)
#SBATCH --error=census_download_%j.err  # Standard error file
#SBATCH --nodes=1                       # Request 1 node
#SBATCH --ntasks=1                      # Request 1 CPU core (adjust if your script can use more)
#SBATCH --mem=16G                       # Request 16GB of memory (adjust based on your data size)
#SBATCH --time=4:00:00                  # Maximum run time (e.g., 4 hours, adjust as needed)
#SBATCH --partition=sigbio            # Specify the partition (queue) if your HPC has them

cd /home/jingqiao/test/

source myenv_py312/bin/activate

/home/jingqiao/test/myenv_py312/bin/python /home/jingqiao/test/download_and_filter.py

deactivate

echo "Job finished at: $(date)"