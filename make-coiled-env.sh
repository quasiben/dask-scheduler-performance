#!/usr/bin/env bash

# Use a post-build script to insert the dask config into the Coiled software environment.

# HACK: Coiled offers no easy way to add auxiliary data files---or a dask config---in software environments,
# so we generate a post-build shell script that has the contents of `dask.yaml` within itself, and writes
# those contents out when executed.
OUT_CONFIG_PATH="~/.config/dask/dask.yaml"

if [[ $1 == "v230" ]]; then
    YAML_CONTENTS=$(<dask-230.yaml)
    ENV_NAME="scheduler-benchmark-230"
    ENV_YML="environment-230.yml"
else
    YAML_CONTENTS=$(<dask.yaml)
    ENV_NAME="scheduler-benchmark"
    ENV_YML="environment.yml"
fi

POSTBUILD_SCRIPT="postbuild.sh"
cat > $POSTBUILD_SCRIPT <<EOF
#!/usr/bin/env sh
set -x

OUT_CONFIG_PATH=$OUT_CONFIG_PATH
# ^ NOTE: no quotes, so ~ expands (https://stackoverflow.com/a/32277036)
mkdir -p \$(dirname \$OUT_CONFIG_PATH)

cat > \$OUT_CONFIG_PATH <<INNER_EOF
$YAML_CONTENTS
INNER_EOF

echo "export DASK_CONFIG=\$OUT_CONFIG_PATH" >> ~/.bashrc

echo "Wrote dask config to \$OUT_CONFIG_PATH:"
cat \$OUT_CONFIG_PATH

wget -q https://github.com/cli/cli/releases/download/v1.7.0/gh_1.7.0_linux_amd64.tar.gz
tar xzf gh_1.7.0_linux_amd64.tar.gz
mv gh_1.7.0_linux_amd64/bin/gh /usr/local/bin
rm gh_1.7.0_linux_amd64.tar.gz
rm -rf gh_1.7.0_linux_amd64
echo "Installed GitHub CLI"
EOF

coiled env create -n $ENV_NAME --conda $ENV_YML --post-build $POSTBUILD_SCRIPT
rm $POSTBUILD_SCRIPT
