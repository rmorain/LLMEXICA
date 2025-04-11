#!/bin/sh
#SBATCH --nodes=1
#SBATCH --gpus=1  
#SBATCH --mem-per-cpu=256G
#SBATCH --time=01:30:00
#SBATCH --ntasks-per-node=4 

#SBATCH -J "Test parsing story"   # job name
#SBATCH --output=/home/rmorain2/git/LLMEXICA/logs/slurm-%j.out
export OLLAMA_MODEL=deepseek-r1:70b
export OLLAMA_DEBUG=1
export OLLAMA_CONTEXT_LENGTH=131072  # Set context length for the model
# Start server with explicit config
ollama serve &
sleep 10
ollama run $OLLAMA_MODEL 
python -u parse_story.py --story_names=princess_and_the_pea,puss_in_boots,the_frog_prince,three_little_pigs,ugly_duckling