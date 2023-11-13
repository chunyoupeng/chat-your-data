#!/bin/bash

# Check if at least one argument is provided
if [ "$#" -eq 0 ]; then
    echo "No arguments provided. Please provide Python scripts to execute."
    exit 1
fi

# Iterate over all arguments
for arg in "$@"
do
    echo "Executing 'run.sh $arg'"
    sh run.sh $arg
done
 