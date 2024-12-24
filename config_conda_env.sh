#!/bin/bash -l

# init conda
eval "$(conda shell.bash hook)"

# Remove env if needed
# conda deactivate
# conda env remove -n limlab-website

# Create the Conda environment
conda env create -f environment.yml -v

# Activate the environment
conda activate limlab-website 

npm install # install packages according to package.json

