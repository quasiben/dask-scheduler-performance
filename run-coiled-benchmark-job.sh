#!/usr/bin/env bash

if ! gh auth status 2> /dev/null; then
    if [ -z $1 ] ; then
        echo "Give your GitHub API token as a command-line argument"
        exit 1
    fi
    echo "$1" | gh auth login --with-token
fi

python nightly-run.py coiled > out.txt

gh gist create *.html *.png out.txt