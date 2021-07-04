#!/bin/bash
# file shall be located in <BASEDIR>/scripts

SCRIPTDIR=$(dirname "$0")
BASEDIR=$SCRIPTDIR/..

# create python virtual env
virtualenv -p python3 $BASEDIR/venv

# activate virtual env
source $BASEDIR/venv/bin/activate

# install pip requirements
pip install -r $BASEDIR/requirements.txt

# create and fill env file
touch $BASEDIR/.env
cat >$BASEDIR/.env <<EOL
QBT_URL=http://127.0.0.1:8081
QBT_USERNAME=admin
QBT_PASSWORD=qbt_password
MEDIA_FILE=data/MediaIndex.json
MAIL_USERNAME=app.dev.notifications.tc@gmail.com
MAIL_PASSWORD=mail_password
ENVIRONMENT=production
DUMP_COMPLETE_DIR=./dump_complete_dir
TV_TARGET_DIR=./tv_target_dir
EOL

# create data files
mkdir $BASEDIR/data

# create empty mediaIndex.json file and fill it with the base json structure
touch $BASEDIR/data/MediaIndex.json
cat >$BASEDIR/data/MediaIndex.json <<EOL
{"media": []}
EOL

# create logs directory
mkdir $BASEDIR/logs

# install cron job
cp $BASEDIR/scripts/media_grab_cronjob.sh /etc/cron.d/media_grab

echo ""
echo "Please remember to update your new .env file."
echo "All done. Enjoy! :)"
