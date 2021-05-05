import yaml

import dask
import distributed

def check_scheduler_is_cythonized(client: distributed.Client):
    # TODO is there a less hacky way to do this?
    path = client.run_on_scheduler(lambda: distributed.scheduler.__file__)
    if not path.endswith(".so"):
        client.shutdown()
        raise RuntimeError(
            f"Scheduler is not Cythonized!\n{path}"
        )

def assert_config_is_superset_of(config: dict, target: dict, context: str = ""):
    for k, v in target.items():
        try:
            check_v = config[k]
        except KeyError:
            msg = f"Config missing expected key {k!r}"
            if context:
                msg = f"{msg} : {context}"
            raise ValueError(msg) from None
        else:
            if isinstance(v, dict):
                assert_config_is_superset_of(check_v, v, context=f"{context}.{k}")
            else:
                if check_v != v:
                    msg = f"Config mismatch: expected {v!r}, found {check_v!r}"
                    if context:
                        msg = f"{msg} : {context}"
                    raise ValueError(msg)


def check_config(client: distributed.Client):
    local_config = dask.config.collect(["dask.yaml"], env={})
    scheduler_config = client.run_on_scheduler(lambda: dask.config.config)

    try:
        assert_config_is_superset_of(scheduler_config, local_config, context="scheduler")
        for worker_id, worker_config in client.run(lambda: dask.config.config).items():
            assert_config_is_superset_of(worker_config, local_config, context=worker_id)
    except ValueError:
        client.shutdown()
        raise
    else:
        scheduler_config.pop("coiled", None)  # has a token in it, don't want it logged
        print(yaml.dump(scheduler_config))
