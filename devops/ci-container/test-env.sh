#!/bin/sh

# pull the new version to be tested
git init
git remote add origin https://github.com/Daniel-Yakov/Gan-Shmoel-Project.git
git pull origin weight
git pull origin billing

# create the container with docker compose
   

# run tests


# Failure - send mails


# Success send maills and deploy new image