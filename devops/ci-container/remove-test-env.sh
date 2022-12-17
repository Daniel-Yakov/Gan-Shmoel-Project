#!/bin/sh

docker-compose -f ./weight/docker-compose-w-test.yml -p test down -v
docker-compose -f ./billing/docker-compose-b-test.yml -p test down -v

