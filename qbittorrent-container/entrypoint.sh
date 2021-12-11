#!/bin/bash

# using https://github.com/bashup/dotenv

# define conf file
CONFIG_FILE=./config-template/qBittorrent.template.conf

# check if temp dir is provided
temp_dir_set=false


# inject variables into qBittorrent.conf
./dotenv.sh -f $CONFIG_FILE set "Downloads\SavePath"=$DUMP_COMPLETE_DIR

if [ -n "$DUMP_TEMP_DIR" ] ; then
    ./dotenv.sh -f $CONFIG_FILE set "Downloads\TempPath"=$DUMP_TEMP_DIR
    ./dotenv.sh -f $CONFIG_FILE set "Downloads\TempPathEnabled"=true
fi

if [ -n "$MAIL_NOTIFICATION_ADDRESS" ]; then
    ./dotenv.sh -f $CONFIG_FILE set "MailNotification\email"=$MAIL_NOTIFICATION_ADDRESS
fi

if [ -n "$MAIL_USERNAME" ]; then
    ./dotenv.sh -f $CONFIG_FILE set "MailNotification\sender"=$MAIL_USERNAME
    ./dotenv.sh -f $CONFIG_FILE set "MailNotification\username"=$MAIL_USERNAME
fi

if [ -n "$MAIL_PASSWORD" ]; then
./dotenv.sh -f $CONFIG_FILE set "MailNotification\password"=$MAIL_PASSWORD
fi

cp config-template/qBittorrent.template.conf /config/qBittorrent.conf

tail -f /dev/null