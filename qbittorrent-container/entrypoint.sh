#!/bin/bash
# using https://github.com/bashup/dotenv

# define conf file
defaultConfigFile=./config-template/qBittorrent.template.conf
targetConfigDir=/config/qBittorrent
targetConfigFile=$targetConfigDir/qBittorrent.conf

# install our default conf file if it has not been updated from the boilerplate version
if [ ! -f $targetConfigFile ]; then
    echo "Installing default qBittorrent.conf file location=$targetConfigFile"
    mkdir -p $targetConfigDir
    cp $defaultConfigFile $targetConfigFile
fi

echo "Starting qbittorrent with new qBittorrent.conf file."

# restart qbittorrent with new config file
/usr/bin/qbittorrent-nox -d
tail -f /config/qBittorrent/logs/qbittorrent.log