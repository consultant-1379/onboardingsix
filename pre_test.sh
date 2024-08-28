#!/bin/bash
# This script is the pre command for jenkins job
# Custom configuration need to be written here
sudo python -m pip install behave==1.2.6
docker stop $(docker ps -a -q) || true
docker rm $(docker ps -a -q) || true
docker-compose -f docker-compose.yml down --rmi all --remove-orphans
docker-compose -f docker-compose.yml build --force-rm
docker-compose -f docker-compose.yml up --build -d