#!/bin/bash -e

deploy_all=false
deploy_backend=false
deploy_frontend=false
# deploy_database=false

print_usage() {
    echo "Usage: $0 [-a] [-b] [-d] [-f] [-h]" >&2;
    echo "options:
        -a Deploy all containers
        -b Deploy backend container
        -f Build and Deploy frontend container
        -h this help message"
    exit 1;
}

while getopts ":abfh" OPTION; do
    case "$OPTION" in
        a) deploy_all=true;;
        b) deploy_backend=true;;
        # d) deploy_database=true;; 
        f) deploy_frontend=true;;
        h)  print_usage;;
        \?) echo "$0: Error: Invalid option: -${OPTARG}" >&2; exit 1;;
        :) echo "$0: Error: option -${OPTARG} requires an argument" >&2; exit 1;;
    esac
done
shift "$(($OPTIND -1))"

echo "all: $deploy_all"
echo "backend: $deploy_backend"
# echo "database: $deploy_database"
echo "frontend: $deploy_frontend"

if $deploy_all; then
    echo "Re-deploy all containers"

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
  
else
    if $deploy_backend; then
        docker compose --profile backend down || true
        docker compose --profile backend up -d
    fi

    if $deploy_frontend; then
        docker compose --profile frontend down || true

        BASE_PATH=$(pwd)
        FRONTEND_PATH="$BASE_PATH/frontend"

        # create vue-builder image
        cd $FRONTEND_PATH
        docker build --network host -t vue-builder -f Dockerfile.build .

        # run vue-builder image to create dist
        docker run --rm -v $FRONTEND_PATH/dist:/root/dist vue-builder
        cd $BASE_PATH
        docker compose --profile frontend up -d --build
    fi

    # if $deploy_database; then
    #     docker compose --profile database down || true
    #     docker compose --profile database up -d
    # fi
fi

