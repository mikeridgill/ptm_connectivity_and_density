#!/bin/bash --login

#SBATCH --job-name=plt_dens
#SBATCH --output=../slurm_output/plot_density.out.%J
#SBATCH --error=../slurm_output/plot_density.err.%J
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
##SBATCH --partition=dev
#SBATCH --mem=250G
#SBATCH --time=22:00:00

module purge
module load python/3.7.0

python3.7 ../python_files/plot_density.py ../input_files/parameters.mat
echo Script completed
