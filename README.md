Media Grab
========

### The Idea ###

This project is designed to automate the download and organisation of media. It can be time-consuming to search for, download and manage your media, this project combats that waste of time by promoting automation. Use the webapp to load up your favourite TV shows and watch them download automatically preventing you ever having to search for a show again.

## Installation

This multi container system is built and run with Docker and docker compose and is configured using an env file. A template for this .env can be found at ./env-template. Simply run:
```
cp ./env-template ./.env
```

to create your own env file, it contains the necessary values that can be customised and some extra values that are left empty but if provided can unlock extra functionality like email notifications, auto episode incrementing and samba network drive mounting.

To build and run the containers:
```
./run.sh
```
from the root directory. This builds the docker network and runs the docker-compose file which stands all the containers up.

After this you can access the web UI from [localhost:5000](localhost:5000) and the qbittorrent UI from [localhost:7002](localhost:7002).

Add a new TV show via the web UI, click Run MediaGrab and watch the download appear in the qbittorrent UI.

After it has downloaded and mediaGrab has run again it will be filed neatly in `./media/TV/<tv_show>/<season_number>/<episode>`.

MediaGrab is also installed as a cronjob, it runs automatically every three hours.

Ideally after you have loaded up your favourite TV shows, you should find them waiting for you as soon as they are released.

Consider installing something like Plex to get the full home Netflix effect.


## FAQs

Q: Why do I have problems running apt install commands in a container?
A: run `sudo nano /etc/default/docker` and make sure the line `DOCKER_OPTS="--dns 8.8.8.8 --dns 8.8.4.4"` is uncommented

## Tests

Tests are located in the `test/` directory, and the unit tests inside the `test/unit_test` directory. Run the tests from the project root directory with this command: `python -m unittest discover -v -s .` after creating and activating a development virtualenv (dependencies are held in `requirements-dev.txt`)

## Bugs

Please report issues via github. Responses will be as quick as possible.

## Licence

This project uses the MIT Licence, found in ./LICENSE

## Disclaimer

This project is not intended to be used for illegal purposes and the consequences of any use of the code in this repository for illegal purposes shall be born solely by the user.
