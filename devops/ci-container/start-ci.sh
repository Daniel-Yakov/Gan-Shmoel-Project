#!/bin/bash

docker rm -f ci
docker build --tag ciimage .
docker run --name ci -p 8080:5000 -d -v /var/run/docker.sock:/var/run/docker.sock ciimage