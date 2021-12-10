#!/bin/bash

# export environment variables to a file so that the app can use them later
printenv > /proj-dir/.env

# run cron in the background
cron

webappRoot=/proj-dir/webapp

cd $webappRoot

uwsgi app.ini