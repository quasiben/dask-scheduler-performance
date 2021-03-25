import os
import dask
import distributed
from datetime import datetime
import numpy as np
import time
from dask.distributed import Client, wait, performance_report
from dask.dataframe.shuffle import shuffle

import xarray as xr
import dask.array as dsa

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import assertions

sns.set(font_scale=1.5, style="whitegrid")


today = datetime.now().strftime("%Y%m%d")


def main(client: Client, filename_suffix: str = ""):
    df = dask.datasets.timeseries(
        start="2000-01-01",
        end="2000-01-31",
        # end="2000-12-31",
        partition_freq="1h",
        freq="60s",
    )
    df = df.persist()
    wait(df)
    iterations = 10

    with performance_report(filename=f"{today}-simple-scheduler{filename_suffix}.html"):
        simple = []
        # print('start simple: ', flush=True)
        for i in range(iterations):
            start = time.perf_counter()
            z = df.x + 1 + 2 - df.y
            z.sum().compute()
            stop = time.perf_counter()
            simple.append(stop - start)
        simple = np.array(simple)

    df2 = None
    with performance_report(filename=f"{today}-shuffle-scheduler{filename_suffix}.html"):
        shuffle_t = []
        # print('start shuffle: ', flush=True)
        for i in range(iterations):
            client.cancel(df2)
            start = time.perf_counter()
            # shuffle(df, "id", shuffle="tasks")
            df2 = df.set_index("id").persist()
            wait(df2)
            stop = time.perf_counter()
            shuffle_t.append(stop - start)
        shuffle_t = np.array(shuffle_t)

    with performance_report(filename=f"{today}-rand-access-scheduler{filename_suffix}.html"):
        rand_access = []
        for i in range(iterations):
            start = time.time()
            df2.head()
            stop = time.time()
            rand_access.append(stop - start)
        rand_access = np.array(rand_access)
    data = dsa.random.random((10000, 1000000), chunks=(1, 1000000))
    da = xr.DataArray(data, dims=['time', 'x'],
                      coords={'day': ('time', np.arange(10000) % 100)})
    clim = da.groupby('day').mean(dim='time')
    anom = da.groupby('day') - clim
    anom_mean = anom.mean(dim='time')
    with performance_report(filename=f"{today}-anom-mean-scheduler{filename_suffix}.html"):
        anom_mean_t = []
        for i in range(iterations):
            start = time.time()
            anom_mean.compute()
            stop = time.time()
            anom_mean_t.append(stop-start)

        anom_mean_t = np.array(anom_mean_t)

    return dict(simple=simple, shuffle=shuffle_t, rand_access=rand_access,
            anom_mean=anom_mean_t)

if __name__ == "__main__":
    import sys

    if sys.argv[-1] == "coiled":
        import coiled
        software = dask.config.get("benchmark.software", "gjoseph92/scheduler-benchmark")
        print(f"Using software environment {software!r} for cluster.")
        start = time.perf_counter()
        cluster = coiled.Cluster(
            # name="scheduler-benchmark",
            n_workers=10,
            worker_memory="54 GiB",
            worker_cpu=1,
            # ^ NOTE: Coiled VM backend required to get these resources
            worker_options={"nthreads": 1},
            scheduler_cpu=1,
            scheduler_memory="8 GiB",
            software=software,
            shutdown_on_close=True,
        )
        elapsed = time.perf_counter() - start
        print(f"Created Coiled cluster in {elapsed / 60:.1f} min")
        client = Client(cluster)
        filename_suffix = "-coiled"
    else:
        client = Client(n_workers=10, threads_per_worker=1)
        filename_suffix = ""

    print(client)
    print(f"Distributed Version: {distributed.__version__}")
    if dask.config.get("benchmark.checks", False):
        assertions.check_scheduler_is_cythonized(client)
        assertions.check_config(client)
    data = main(client, filename_suffix=filename_suffix)
    client.shutdown()

    today = datetime.now().strftime("%Y%m%d")

    bench_data_name = f"benchmark-historic-runs{filename_suffix}.csv"
    bench_image = f"{today}-benchmark-history{filename_suffix}.png"
    if os.path.exists("/etc/dgx-release"):
        bench_data_name = "dgx-" + bench_data_name
        bench_image = "dgx-" + bench_image


    for idx, (k, v) in enumerate(data.items()):
        print(k)
        mean = np.format_float_scientific(v.mean(), precision=3)
        std = np.format_float_scientific(v.std(), precision=3)
        with open(bench_data_name, "a+") as f:
            f.write(f"{today},{k},{v.mean()},{v.std()}\n")

        print(f"\t {mean} +/- {std}")

    print("\n\n## Raw Values")
    for k, v in data.items():
        print(k)
        print(f"\t {v}")

    fig, ax = plt.subplots(1, 4, figsize=(10, 10))
    df = pd.read_csv(
        bench_data_name,
        parse_dates=["date"],
        names=["date", "operation", "avg", "std"],
    )
    ax[0].set_ylabel("Time (s)")
    for idx, (key, group) in enumerate(df.groupby("operation")):
        ax[idx].set_title(f"{key}")
        ax[idx].errorbar(group.date, group.avg, yerr=group["std"].values)
        lim = group.avg.max() + group["std"].max()
        ax[idx].set_ylim(0, lim)
        plt.setp(ax[idx].get_xticklabels(), rotation=45)

    plt.savefig(bench_image)
