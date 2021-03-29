#!/bin/bash

SCRIPTDIR=$(dirname "$0")

# create python virtual env
virtualenv $SCRIPTDIR/venv

# activate virtual env
source $SCRIPTDIR/venv/bin/activate

# install pip requirements
pip install -r $SCRIPTDIR/requirements.txt

# create and fill env file
touch $SCRIPTDIR/.env
cat >$SCRIPTDIR/.env <<EOL
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
mkdir $SCRIPTDIR/data

touch $SCRIPTDIR/data/MediaIndex.json
cat >$SCRIPTDIR/data/MediaIndex.json <<EOL
{"media": []}
EOL

touch $SCRIPTDIR/data/DownloadsInProgress.json
cat >$SCRIPTDIR/data/DownloadsInProgress.json <<EOL
{"tv-seasons": [], "tv-episodes": []}
EOL

# create logs directory
mkdir $SCRIPTDIR/logs

# install cron job
cp $SCRIPTDIR/scripts/media_grab_cronjob.sh /etc/cron.d/media_grab

echo ""
echo "Please remember to update your new .env file."
echo "All done. Enjoy! :)"

# setup cronjob to run program periodically
