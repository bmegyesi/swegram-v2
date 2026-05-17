#!/bin/bash
# Build script for the backend

# Create pip package for swegram
rm -rf .venv dist build
python3 -m venv .venv
source .venv/bin/activate

pip install wheel build
pip install -r requirements.txt

python3 -m build --wheel

# Create docker image
version=$(python3 -c "from swegram_main.version import VERSION; print(VERSION)")
docker build -t rex0046/swegram-backend:$version --build-arg VERSION=$version .
