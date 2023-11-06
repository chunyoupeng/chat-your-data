#!/bin/bash

# This is the variable that we will pass to the Python functions
VAR="$1"

# Call the Python script with the function name and the variable
python ingest_data.py "$VAR"
python file_app.py "$VAR"
python final.py "$VAR"
