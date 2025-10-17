#!/bin/bash

OUTPUT_FILE="output_twee.txt"
TWEE="./twee.sh"
SUCCESS_STRING="RESULT: Theorem (the conjecture is true)"

if [ -f $OUTPUT_FILE ]; then
    rm $OUTPUT_FILE
fi

for x in $(ls data)
do
    echo Starting with data/$x:
    cat rules.p data_twee/$x | $TWEE 1 - > o.txt
    # check that the output contains the success string
    if grep -q "$SUCCESS_STRING" o.txt; then
        echo Success
        echo Success >> $OUTPUT_FILE
    else
        echo Failure
        # echo Failure >> $OUTPUT_FILE
    fi
    echo
done
