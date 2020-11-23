#!/bin/bash
set -xo pipefail

# load aliases like module
source /etc/profile

#export PATH=/gpfs/fs1/bzaitlen/miniconda3/bin:$PATH
CONDA_ROOT=/gpfs/fs1/bzaitlen/miniconda3
if test -f ~/.profile; then
        source ~/.profile
    fi
source $CONDA_ROOT/etc/profile.d/conda.sh
TODAY=`date +"%Y%m%d"`
ENV="$TODAY-nightly-0.17"

conda activate $ENV
which python

python nightly-run.py > dgx_raw_data.txt
echo "Copy sitecustomize.py..."
cp sitecustomize.py ${CONDA_PREFIX}/lib/python3.8/sitecustomize.py
bash run-shuffle.sh
python publish_benchmark.py
echo "Clean up sitecustomize.py..."
rm ${CONDA_PREFIX}/lib/python3.8/sitecustomize.py
echo ALL_DONE
