#!/bin/bash

set -xo pipefail

cd ~/GitRepos/dask-scheduler-performance/nightly-benchmark
job_id=$(sbatch -N 1 --parsable --wait run-dgx-benchmark.sh)
