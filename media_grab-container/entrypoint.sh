#!/bin/bash

# export environment variables to a file so that the app can use them later
printenv > /proj-dir/.env

# create MediaIndex.json if it does not exist
if [ ! -f /data/MediaIndex.json ]; then
    cp ./templates/MediaIndex-template.json /data/MediaIndex.json
fi

# run cron in the background
cron

webappRoot=/proj-dir/webapp

cd $webappRoot

uwsgi app.ini