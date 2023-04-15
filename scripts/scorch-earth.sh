#!/bin/bash

# stop the containers
docker stop nginx-container qbittorrent-container media_grab-container

# remove the containers
docker container prune

# remove the volumes
docker volume rm data-volume media-volume media_grab_media-volume

# rebuild without cache
# docker-compose -f docker-compose.yml -f docker-compose.directory.yml build --no-cache

# remove the networks
docker network rm media_grab_webapp_default