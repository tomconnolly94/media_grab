#!/bin/bash
CURRENTDIR=$(dirname "$0")
BASEDIR=$CURRENTDIR/..

# stop and remove container
docker stop media_grab && docker rm media_grab

# build
docker build -t media_grab $BASEDIR

# run
docker run -d --name media_grab --mount type=bind,source=/mnt/netShare,target=/netShare -t media_grab