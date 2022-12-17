#!/bin/sh

# pull the new version to be tested
git init
git remote add origin https://github.com/Daniel-Yakov/Gan-Shmoel-Project.git
git pull origin main

# create the containers with docker compose

export WEIGHT_APP_PORT=8081
export BILLING_APP_PORT=8082
export NETWORK=test-env

#  create test-env docker-compose files
cp ./weight/docker-compose.yaml ./weight/docker-compose-w-test.yml
cp ./billing/docker-compose.yml ./billing/docker-compose-b-test.yml

# weight app
docker-compose -f ./weight/docker-compose-w-test.yml build --no-cache
docker-compose -f ./weight/docker-compose-w-test.yml -p test up -d

# billing app
docker-compose -f ./billing/docker-compose-b-test.yml build --no-cache
docker-compose -f ./billing/docker-compose-b-test.yml -p test up -d

# run tests
./weight/test.sh > report.txt
let weight_test=$?

./billing/test.sh >> report.txt
let billing_test=$?

exit $(($billing_test + $weight_test))

