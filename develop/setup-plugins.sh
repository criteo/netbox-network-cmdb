#!/bin/bash

set -e

for dir in ./netbox*; do
    if [ -d "$dir" ] && [ -f "${dir}/setup.py" ]; then
    	cd $dir && pip install -e . --user && cd ../
    fi
done
