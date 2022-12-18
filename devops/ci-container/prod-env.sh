#!/bin/sh

export WEIGHT_APP_PORT=8089
export BILLING_APP_PORT=8090
export NETWORK=prod-env

# remove prevoius prod container
docker-compose -f ./weight/docker-compose-w-test.yml -p prod down
docker-compose -f ./billing/docker-compose-b-test.yml -p prod down

# create new prod contianers
docker-compose -f ./weight/docker-compose-w-test.yml -p prod up -d --build
docker-compose -f ./billing/docker-compose-b-test.yml -p prod up -d --build

rm -rf ./weight/docker-compose-w-test.yml ./billing/docker-compose-b-test.yml

docker rmi $(docker images -q)