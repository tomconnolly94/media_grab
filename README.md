Media Grab
========

### The Idea ###

This project is designed to automate the download and organisation of media. It can be time-consuming to search for, download and manage your media, this project combats that waste of time by promoting automation. Configure the project using a json and .env files, install it on an always-on machine like a raspberry pi, let it run with the provided cronjob and let it find all of your favourite media.

### Requirements ### 


## Installation

### Linux

To install on a linux system simply run the script `install.sh` found in in the `scripts/` directory. This will:

* Create a virtualenv and install all pip dependencies.
* Create an .env file and write default values (which must be updated) to it. This file holds many different configuration values including the torrent server address and the directories to store the torrents to.
* Create and add default content to the `data/MediaIndex.json` file. This file will hold a json object containing details about the media you are interested in downloading.
* Create a `logs/` dir which will be used to store rotating log files.
* Install the cronjob to the `/etc/cron.d/` directory.

### Windows & MacOS

Not currently supported

## Tests

Tests are located in the `test/` directory, and the unit tests inside the `test/unit_test` directory. Run the tests from the project root directory with this command: `python -m unittest discover -v -s .`

## Licence

This project uses the fairly permissive MIT Licence, found in ./LICENSE

## Disclaimer

This project is not intended to be used for illegal purposes and the consequences of any use of the code in this repository for illegal purposes shall be born solely by the user.