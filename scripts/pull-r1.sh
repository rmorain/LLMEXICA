#!/bin/sh
#SBATCH --qos=login
#SBATCH --mem=64G
#SBATCH --time=2:00:00
#SBATCH -J "Pull R1"   # job name
#SBATCH --output=/home/rmorain2/git/LLMEXICA/logs/slurm-%j.out
ollama serve &
sleep 10
ollama pull deepseek-r1:671b