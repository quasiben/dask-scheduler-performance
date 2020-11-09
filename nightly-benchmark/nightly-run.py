import dask
import distributed
from datetime import datetime
import numpy as np
import time
from dask.distributed import Client, wait, performance_report
from dask.dataframe.shuffle import shuffle


today = datetime.now().strftime("%Y%m%d")

def main():
    client = Client(n_workers=10)

    df = dask.datasets.timeseries(
		start="2000-01-01",
                end="2000-01-31",
                # end="2000-12-31",
                partition_freq="1h",
                freq="60s",
            )
    df = df.persist()
    wait(df)
    iterations = 3

    with performance_report(filename=f'{today}-simple-scheduler.html'):
        simple = []
        for i in range(iterations):
            start = time.time()
            z = df.x + 1 + 2 - df.y
            z.sum().compute()
            stop = time.time()
            simple.append(stop-start)
        simple = np.array(simple)

    df2 = df.head()
    with performance_report(filename=f'{today}-shuffle-scheduler.html'):
        shuffle_t = []
        for i in range(iterations):
            client.cancel(df2)
            start = time.time()
            #shuffle(df, "id", shuffle="tasks")
            df2 = df.set_index("id").persist()
            wait(df2)
            stop =  time.time()
            shuffle_t.append(stop-start)
        shuffle_t = np.array(shuffle_t)


    with performance_report(filename=f'{today}-rand-access-scheduler.html'):
        rand_access = []
        for i in range(iterations):
            start = time.time()
            df2.head()
            stop = time.time()
            rand_access.append(stop-start)
        rand_access = np.array(rand_access)
    return dict(simple=simple, shuffle=shuffle_t, rand_access=rand_access)

if __name__ == "__main__":
    data = main()
    print(f"Dask Version: {dask.__version__}")
    print(f"Distributed Version: {distributed.__version__}")

    today = datetime.now().strftime("%Y%m%d")
    history_file = "benchmark-historic-runs.csv"

    for idx, (k, v) in enumerate(data.items()):
        print(k)
        mean = np.format_float_scientific(v.mean(), precision=3)
        std = np.format_float_scientific(v.std(), precision=3)
        with open(history_file, "a+") as f:
            f.write(f"{today},{k},{v.mean()},{v.std()}\n")

        print(f"\t {mean} +/- {std}")

    print("\n\n## Raw Values")
    for k, v in data.items():
        print(k)
        print(f"\t {v}")

