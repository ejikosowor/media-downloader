#!/bin/bash

# abort on errors
set -e

# Create and activate virtual env
source "virtual/bin/activate"

# Install dependencies
pip3 install -r requirements.txt

# Deactivate virtual env
deactivate

# Make start.sh executable
sudo chmod +x ./start.sh

exit 1