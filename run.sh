#!/bin/bash -e

BASE_PATH=$(pwd)
FRONTEND_PATH="$BASE_PATH/frontend"
user=$(whoami)

# create vue-builder image
cd $FRONTEND_PATH
docker build --network host -t vue-builder -f Dockerfile.build .

# run vue-builder image to create dist
docker run --rm -v $FRONTEND_PATH/dist:/root/dist vue-builder

# change ownership for dist generated from vue-builder
chown -R $user:$user dist


# Create swegram-backend image
cd $BASE_PATH
docker build --network host -t swegram-backend .


# Start the containers with help of docker compose
# remove data (mysql container generates data folder)
rm -rf data
docker compose --profile client up -d
