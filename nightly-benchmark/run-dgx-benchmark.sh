#!/bin/bash
set -xo pipefail

# load aliases like module
source /etc/profile

#export PATH=/gpfs/fs1/bzaitlen/miniconda3/bin:$PATH
CONDA_ROOT=/gpfs/fs1/bzaitlen/miniconda3
if test -f ~/.profile; then
        source ~/.profile
fi

# Environment creation happens in a SLURM job here:
# https://github.com/quasiben/dask-cuda-benchmarks/blob/main/slurm/create-env.sh
source $CONDA_ROOT/etc/profile.d/conda.sh
TODAY=`date +"%Y%m%d"`
ENV="$TODAY-nightly-0.17"

conda activate $ENV
which python

echo "Cythonize Distributed"
pushd "${CONDA_PREFIX}/lib/python3.8/site-packages/"
cythonize -f -i -3 --directive="profile=True" \
	"distributed/scheduler.py" \

popd

srun -N1 python nightly-run.py > dgx_raw_data.txt
echo "Copy sitecustomize.py..."
cp sitecustomize.py ${CONDA_PREFIX}/lib/python3.8/sitecustomize.py
export DASK_OPTIMIZATION__FUSE__ACTIVE=False
srun -N1 bash run-shuffle.sh
srun -N1 python publish_benchmark.py
echo "Clean up sitecustomize.py..."
rm ${CONDA_PREFIX}/lib/python3.8/sitecustomize.py
rm *pstat*
echo ALL_DONE
