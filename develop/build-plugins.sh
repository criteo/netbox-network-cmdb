#!/bin/bash

set -e

BUILD_DIR=/sdist/

for dir in ./netbox*; do
    if [ -d "$dir" ] && [ -f "${dir}/setup.py" ]; then
        cd $dir && python setup.py sdist -d $BUILD_DIR && cd ../
    fi
done
