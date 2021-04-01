"""
Run the benchmark script within Coiled, as well as the cluster.

Currently we do this through a Jupyter notebook, since I'm not sure the right way
to securely get a GitHub API token into a Coiled Job. So for now, you create the notebook
configs (which use the same software env as the cluster, including the correct dask config baked in),
go to https://cloud.coiled.io/gjoseph92/notebooks to launch the notebook(s), then in a terminal::

    $ chmod +x run-coiled-benchmark-job.sh
    $ bash  # the jupyter terminal is currently opening in `sh`; only bash has our conda env set
    $ ./run-coiled-benchmark-job.sh <github-api-token>

This will run the benchmark and upload all the outputs to a gist.

Apparently the jobs don't stop (Jupyter doesn't terminate?) even via the "shut down" menu option, so I'm
just doing `[coiled.stop_job(j) for j in coiled.list_jobs()]` to stop all the notebooks once they're done.

Clearly all this will be more reasonable as a plain Job, once we figure out the secrets situation.
"""

import coiled

NIGHTLY_JOB = "scheduler-benchmark"
V230_JOB = "scheduler-benchmark-230"

def create_notebook(v230=False):
    coiled.create_job_configuration(
        name=(V230_JOB if v230 else NIGHTLY_JOB) + "-nb",
        software="gjoseph92/scheduler-benchmark-230" if v230 else "gjoseph92/scheduler-benchmark",
        cpu=1,
        memory="4 GiB",
        command=["jupyter", "lab", "--allow-root", "--ip=0.0.0.0", "--no-browser"],
        # TODO why does this start in `sh` and not `bash`?
        ports=[8888],
        files=["nightly-benchmark/nightly-run.py", "nightly-benchmark/assertions.py", "run-coiled-benchmark-job.sh"],
    )

def create_job_config(v230=False):
    coiled.create_job_configuration(
        name=V230_JOB if v230 else NIGHTLY_JOB,
        software="gjoseph92/scheduler-benchmark-230" if v230 else "gjoseph92/scheduler-benchmark",
        cpu=1,
        memory="4 GiB",
        command=["python", "nightly-run.py", "coiled"],
        # TODO how to securely add a github api token so we can run the script instead, and upload the gist?
        # then this will actually work as a fire-and-forget job.
        files=["nightly-benchmark/nightly-run.py", "nightly-benchmark/assertions.py", "run-coiled-benchmark-job.sh"],
    )

def run_job(v230=False):
    coiled.start_job(V230_JOB if v230 else NIGHTLY_JOB)

if __name__ == "__main__":
    # TODO also create job configs, once we can get secrets into coiled jobs.
    create_notebook(v230=False)
    create_notebook(v230=True)