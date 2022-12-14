#!/bin/bash

docker build --t start-CI .
docker run -d -p 8080:5000 start-CI