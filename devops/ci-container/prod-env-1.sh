#!/bin/bash
docker stop billing_pythonapp_1
docker stop billing_mysql_1
docker rm billing_pythonapp_1
docker rm billing_mysql_1
docker stop weight_app_weight_1
docker stop weight_my_data_1
docker rm weight_app_weight_1
docker rm weight_my_data_1
docker rmi $(docker image ls)
# ??? docker network rm prod-net ??? 
# ??? docker network create prod-net ???
# ??? git pull origin/main ???
docker-compose -f ./weight/docker-compose.yml up -d
docker-compose -f ./billing/docker-compose.yml up -d
docker-start billing_pythonapp_1
docker-start weight_app_weight_1
