#!/bin/bash

TODAY=`date +"%Y%m%d"`
dask-scheduler --scheduler-file sched.json &
SCHED_PID=$!
sleep 0.5
dask-worker --scheduler-file sched.json --nprocs 4 --nthreads 1 &
sleep 0.5
time python shuffle.py
CLIENT_PID=$!
sleep 10
echo $SCHED_PID
echo $CLIENT_PID

gprof2dot -f pstats prof_${SCHED_PID}.pstat | dot -Tpng -o ${TODAY}-sched-graph.png
CLIENT_PROF=`find . -iname "*.pstat" -execdir grep -l "persist" {} +`
gprof2dot -f pstats ${CLIENT_PROF} | dot -Tpng -o ${TODAY}-client-graph.png
