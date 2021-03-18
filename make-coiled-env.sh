#!/usr/bin/env bash

# # Use a post-build script to insert the dask config into the Coiled software environment.

# # HACK: Coiled offers no easy way to add auxiliary data files---or a dask config---in software environments,
# # so we generate a post-build shell script that has the contents of `dask.yaml` within itself, and writes
# # those contents out when executed.
# OUT_CONFIG_PATH="~/.config/dask/dask.yaml"

# YAML_CONTENTS=$(<dask.yaml)
# POSTBUILD_SCRIPT="postbuild.sh"
# cat > $POSTBUILD_SCRIPT <<EOF
# #!/usr/bin/env sh
# set -x

# OUT_CONFIG_PATH=$OUT_CONFIG_PATH
# # ^ NOTE: no quotes, so ~ expands (https://stackoverflow.com/a/32277036)
# mkdir -p \$(dirname \$OUT_CONFIG_PATH)

# cat > \$OUT_CONFIG_PATH <<INNER_EOF
# $YAML_CONTENTS
# INNER_EOF

# echo "export DASK_CONFIG=\$OUT_CONFIG_PATH" >> ~/.bashrc

# echo "Wrote dask config to \$OUT_CONFIG_PATH:"
# cat \$OUT_CONFIG_PATH
# EOF

coiled env create -n scheduler-benchmark --conda environment.yml
# rm $POSTBUILD_SCRIPT
