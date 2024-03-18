#!/bin/bash

version=$(cat docker/version)
docker login -u rex0046 -p $(cat swegram.token)
docker build --network host -t rex0046/swegram-backend:$version .
docker push rex0046/swegram-backend:$version
