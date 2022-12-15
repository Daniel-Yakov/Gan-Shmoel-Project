#!/bin/sh

docker-compose -f ./weight/docker-compose.yaml down -v
docker-compose -f ./billing/docker-compose.yml down -v

