#!/bin/bash

# create python virtual env
virtualenv venv

# activate virtual env
source venv/bin/activate

# install pip requirements
pip install -r requirements.txt

# create and fill env file
touch .env
cat >.env <<EOL
QBT_URL=http://127.0.0.1:8081
QBT_USERNAME=admin
QBT_PASSWORD=qbt_password
MEDIA_FILE=data/MediaIndex.json
DOWNLOADS_IN_PROGRESS_FILE=data/DownloadsInProgress.json
MAIL_USERNAME=app.dev.notifications.tc@gmail.com
MAIL_PASSWORD=mail_password
ENVIRONMENT=production
DUMP_COMPLETE_DIR=./dump_complete_dir
TV_TARGET_DIR=./tv_target_dir
EOL

# create data files
mkdir data

touch data/MediaIndex.json
cat >data/MediaIndex.json <<EOL
{"media": []}
EOL

touch data/DownloadsInProgress.json
cat >data/DownloadsInProgress.json <<EOL
{"tv-seasons": [], "tv-episodes": []}
EOL

# create logs directory
mkdir logs

echo "Please remember to update your new .env file."

# setup cronjob to run program periodically
