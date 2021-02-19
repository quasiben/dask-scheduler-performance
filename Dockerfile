FROM continuumio/miniconda3:4.9.2

RUN conda create -n perf-dev -c conda-forge \
    python=3.8 \
    dask \
    distributed \
    compilers \
    Cython \
    uvloop \
    ipython \
    viztracer \
    && conda clean --all -y \
    && echo "conda activate perf-dev" >> ~/.bashrc

# Ensure subsequent RUN commands happen within the perf-dev conda environment
SHELL ["conda", "run", "-n", "perf-dev", "/bin/bash", "-c"]

# Install development versions of dask and (cythonized) distributed
RUN conda uninstall --force dask distributed \
    && python -m pip install git+https://github.com/dask/dask.git@master \
    && git clone https://github.com/dask/distributed.git \
    && cd distributed \
    && python -m pip install -vv --no-deps --install-option="--with-cython=profile" .