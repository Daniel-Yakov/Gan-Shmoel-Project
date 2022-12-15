#!/bin/bash

# docker rm -f ci (stop)
docker build --tag ciimage .
docker run --name ci -p 8080:5000 -d -v /var/run/docker.sock:/var/run/docker.sock ciimage
docker network create test-env
docker network create prod-env