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

sns.set(font_scale=1.5, style="whitegrid")


today = datetime.now().strftime("%Y%m%d")


def main():
    client = Client(n_workers=10, threads_per_worker=1)
    print(client)

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

    with performance_report(filename=f"{today}-simple-scheduler.html"):
        simple = []
        # print('start simple: ', flush=True)
        for i in range(iterations):
            start = time.time()
            z = df.x + 1 + 2 - df.y
            z.sum().compute()
            stop = time.time()
            simple.append(stop - start)
        simple = np.array(simple)

    df2 = None
    with performance_report(filename=f"{today}-shuffle-scheduler.html"):
        shuffle_t = []
        # print('start shuffle: ', flush=True)
        for i in range(iterations):
            client.cancel(df2)
            start = time.time()
            # shuffle(df, "id", shuffle="tasks")
            df2 = df.set_index("id").persist()
            wait(df2)
            stop = time.time()
            shuffle_t.append(stop - start)
        shuffle_t = np.array(shuffle_t)

    with performance_report(filename=f"{today}-rand-access-scheduler.html"):
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
    with performance_report(filename=f"{today}-anon-mean-scheduler.html"):
        anon_mean_t = []
        for i in range(iterations):
            start = time.time()
            anom_mean.compute()
            stop = time.time()
            anon_mean_t.append(stop-start)

        anon_mean_t = np.array(anon_mean_t)

    return dict(simple=simple, shuffle=shuffle_t, rand_access=rand_access,
            anon_mean=anon_mean_t)

if __name__ == "__main__":
    data = main()
    print(f"Distributed Version: {distributed.__version__}")

    today = datetime.now().strftime("%Y%m%d")

    bench_data_name = "benchmark-historic-runs.csv"
    bench_image = f"{today}-benchmark-history.png"
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
    for idx, (key, group) in enumerate(df.groupby("operation")):
        ax[idx].set_title(f"{key}")
        ax[idx].errorbar(group.date, group.avg, yerr=group["std"].values)
        lim = group.avg.max() + group["std"].max()
        ax[idx].set_ylim(0, lim)
        plt.setp(ax[idx].get_xticklabels(), rotation=45)

    plt.savefig(bench_image)
