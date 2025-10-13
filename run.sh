#!/bin/bash

rm output.txt

for x in $(ls data)
do
    echo Starting with data/$x:
    timeout 0.5s ~/knuth_bendix_egraph/target/release/main -r "rules.rule" -t "data/$x" > o.txt
    t=$(cat o.txt | grep -A 1 "Extracted term" | tail -n 1)
    hal="${x:5:1}"
    if [[ "NUM$hal" == "$t" ]]; then
        echo Success
        echo Success >> output.txt
    fi
    echo
done
