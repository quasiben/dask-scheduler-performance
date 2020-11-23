#!/bin/bash


source ~/.bashrc
CONDA_ROOT=~/miniconda3
if test -f ~/.profile; then
    source ~/.profile
fi

source $CONDA_ROOT/etc/profile.d/conda.sh
conda activate dask-dev
which python

python nightly-run.py > raw_data.txt
python publish_benchmark.py

