#!/bin/bash

# get script dir
SCRIPTDIR=$(dirname "$0")

# pull latest code
git pull

# stop the containers
docker stop nginx-container qbittorrent-container media_grab-container

# remove the containers
docker container prune

# remove the media volume
docker volume rm media-volume

# move to project root
cd $SCRIPTDIR/..

# rebuild and restart containers in daemon mode
docker-compose -f docker-compose.yml -f docker-compose.samba.yml up --build

cd -
