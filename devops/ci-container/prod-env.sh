#!/bin/sh

export WEIGHT_APP_PORT=8089
export BILLING_APP_PORT=8090
export NETWORK=prod-env

# cp ./weight/docker-compose.yaml ./weight/docker-compose-w-prod.yml
# cp ./billing/docker-compose.yml ./billing/docker-compose-b-prod.yml

# remove prevoius prod container
docker-compose -f ./weight/docker-compose-w-test.yml -p prod down
docker-compose -f ./billing/docker-compose-b-test.yml -p prod down

# create new prod contianers
docker-compose -f ./weight/docker-compose-w-test.yml -p prod up -d --build
docker-compose -f ./billing/docker-compose-b-test.yml -p prod up -d --build

# rm ./weight/docker-compose-w-prod.yml ./billing/docker-compose-b-prod.yml
rm -rf ./weight/docker-compose-w-test.yml ./billing/docker-compose-b-test.yml