#!/bin/bash

# export environment variables in a file
printenv | grep -v “no_proxy” >> /etc/environment

# run cron in the foreground to keep the container running
cron -f