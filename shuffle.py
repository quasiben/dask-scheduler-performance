from dask.datasets import timeseries
import time
from dask.dataframe.shuffle import shuffle
from dask.distributed import Client, wait

if __name__ == "__main__":
    client = Client("127.0.0.1:8786")
    ddf_h = timeseries(start='2000-01-01', end='2000-01-02', partition_freq='1min')
    result = shuffle(ddf_h, "id", shuffle="tasks")
    for i in range(20):
        ddf = client.persist(result)
        _ = wait(ddf)
        client.cancel(ddf)
    client.shutdown()
    time.sleep(0.5)
