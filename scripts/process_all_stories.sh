#!/bin/sh
#SBATCH --nodes=1
#SBATCH --gpus=h200:4  # Minimum required for 671b model
#SBATCH --mem-per-cpu=256G
#SBATCH --time=6:00:00
#SBATCH --ntasks-per-node=4 

#SBATCH -J "Parse all stories"   # job name
#SBATCH --output=/home/rmorain2/git/LLMEXICA/logs/slurm-%j.out
export OLLAMA_MODEL=deepseek-r1:671b
# export OLLAMA_MODEL=deepseek-r1:70b
export OLLAMA_DEBUG=1
# export OLLAMA_CONTEXT_LENGTH=131072  # Set context length for the model
# export OLLAMA_CONTEXT_LENGTH=32768  # Set context length for the model
export OLLAMA_CONTEXT_LENGTH=15000  # Set context length for the model
# Start server with explicit config
ollama serve &
sleep 10
ollama run $OLLAMA_MODEL 
python -u parse_story.py 