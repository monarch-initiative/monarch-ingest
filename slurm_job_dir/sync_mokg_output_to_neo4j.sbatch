#!/bin/bash
# Job name:
#SBATCH --job-name=test
#
# Account:
#SBATCH --account=dkorn
#
# Partition:
#SBATCH --partition=batch

# Output:
#SBATCH --output=/home/dkorn/MODEL_ORGANISM_MODULAR_INGEST/monarch-ingest/slurm_job_dir/OUTPUT/slurm-%j.out
#SBATCH --error=/home/dkorn/MODEL_ORGANISM_MODULAR_INGEST/monarch-ingest/slurm_job_dir/OUTPUT/slurm-%j.err

#
# Request one node:
#SBATCH --nodes=1
#
# Specify one task:
#SBATCH --ntasks-per-node=1
#
# Number of processors for single task needed for use case (example):
#SBATCH --cpus-per-task=4
#
# Wall clock limit:
#SBATCH --time=00:00:30
#
#Memory
#SBATCH --mem=40G

## Command(s) to run (example):
poetry run kgx