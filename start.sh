#!/bin/bash
# abort on errors
set -e

project_base="/home/priest/media-downloader-main"

cd $project_base

source "virtual/bin/activate"
streamlit run main.py --server.address 127.0.0.1 --server.headless true --server.port 8500