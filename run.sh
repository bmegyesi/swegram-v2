#!/bin/bash -e

#clean up possible old containers
docker compose --profile client down

BASE_PATH=$(pwd)
FRONTEND_PATH="$BASE_PATH/frontend"

# create vue-builder image
cd $FRONTEND_PATH
docker build --network host -t vue-builder -f Dockerfile.build .

# run vue-builder image to create dist
docker run --rm -v $FRONTEND_PATH/dist:/root/dist vue-builder

# Start the containers with help of docker compose
# remove data (mysql container generates data folder)
docker compose --profile client up -d --build
