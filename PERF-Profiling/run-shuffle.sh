sudo perf record $CONDA_PREFIX/bin/dask-scheduler &
sleep 0.5
dask-worker 127.0.0.1:8786 --nprocs 10 &
sleep 0.5
time python shuffle.py
sleep 0.5
sudo perf report -i perf.data --force | head -n 20
sleep 0.5
