#!/bin/bash

# export environment variables to a file so that an app can explicitly import them later
printenv > /proj-dir/.env

# run cron in the background
cron

webappRoot=/proj-dir/webapp

cd $webappRoot

uwsgi app.ini