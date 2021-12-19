from dask.datasets import timeseries
import time
from dask.dataframe.shuffle import shuffle
from dask.distributed import Client, wait

if __name__ == "__main__":
    client = Client("127.0.0.1:8786")
    ddf_h = timeseries(start='2000-01-01', end='2000-01-02', partition_freq='1min')
    for i in range(20):
        print("Iteration: ", i)
        s = ddf_h["id"] + 10
        mean = s.mean()
        mean = client.persist(mean)
        _ = wait(mean)
        client.cancel(mean)
        client.cancel(s)
    client.shutdown()
    time.sleep(0.5)
