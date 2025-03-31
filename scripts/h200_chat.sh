#!/bin/sh
#SBATCH --nodes=1
#SBATCH --gpus=h200:4  # Minimum required for 671b model
#SBATCH --mem-per-cpu=512G
#SBATCH --time=01:00:00
#SBATCH --ntasks-per-node=4  # Critical for H200 tensor parallelism

#SBATCH -J "H200 Chat"   # job name
#SBATCH --output=/home/rmorain2/git/LLMEXICA/logs/slurm-%j.out
export OLLAMA_MODEL=deepseek-r1:671b
export OLLAMA_DEBUG=1
# Start server with explicit config
ollama serve &
sleep 10
ollama run deepseek-r1:671b
python chat.py