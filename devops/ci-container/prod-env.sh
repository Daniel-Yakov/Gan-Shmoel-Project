#!/bin/sh


# remove prevoius prod container
docker-compose -f ./weight/docker-compose.yaml down
docker-compose -f ./billing/docker-compose.yml down

export WEIGHT_APP_PORT=8089
export BILLING_APP_PORT=8090
export NETWORK=prod-env

# create new prod contianers
docker-compose -f ./weight/docker-compose.yaml up -d
docker-compose -f ./billing/docker-compose.yml up -d

