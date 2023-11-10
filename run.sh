#!/bin/bash

# This is the variable that we will pass to the Python functions
VAR="$1"

# Call the Python script with the function name and the variable
python chat_paper/ingest_data.py "$VAR"
python chat_paper/file_app.py "$VAR"
python chat_paper/final.py "$VAR"
