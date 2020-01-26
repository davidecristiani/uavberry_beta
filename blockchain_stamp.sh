##!/usr/bin/env bash

for filename in ./web_monitor/inventories/*.yaml; do
    if [ ! -f "$filename.ots" ]
    then
        echo "It's time to  timestamp $filename"
        ots stamp "$filename"
    fi
done
