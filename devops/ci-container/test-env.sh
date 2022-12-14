#!/bin/sh

# pull the new version to be tested
git init
git remote add origin https://github.com/Daniel-Yakov/test-env.git
git pull origin main

# create the containers with docker compose

export WEIGHT_APP_PORT=8081
export BILLING_APP_PORT=8082

# weight app
docker-compose -f ./weight/docker-compose.yaml build --no-cache
docker-compose -f ./weight/docker-compose.yaml up -d

# billing app
docker-compose -f ./billing/docker-compose.yml build --no-cache
docker-compose -f ./billing/docker-compose.yml up -d


# run tests



