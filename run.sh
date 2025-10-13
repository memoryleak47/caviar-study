#!/bin/bash

function f() {
    ~/knuth_bendix_egraph/target/release/main -r "rules.rule" -t "data/$1" > o.txt
}

for x in $(ls data)
do
    echo Starting with data/$x:
    timeout 3s f $x
done
