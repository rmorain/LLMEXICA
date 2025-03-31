#!/bin/sh
#SBATCH --qos=test
#SBATCH --gpus=6
#SBATCH --mem=64G
#SBATCH --time=2:30:00
#SBATCH -J "Chat"   # job name
#SBATCH --output=/home/rmorain2/git/LLMEXICA/logs/slurm-%j.out
export OLLAMA_MODEL=deepseek-r1:671b
ollama serve &
sleep 10
# ollama run deepseek-r1:7b
ollama run deepseek-r1:671b
python chat.py