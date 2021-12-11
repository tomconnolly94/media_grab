#!/bin/bash

docker network create media_grab_webapp_default

docker-compose -f docker-compose.yml -f docker-compose.directory.yml up --build -d