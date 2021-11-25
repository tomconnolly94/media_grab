Media Grab
========

### The Idea ###

This project is designed to automate the download and organisation of media. It can be time-consuming to search for, download and manage your media, this project combats that waste of time by promoting automation. Configure the project using a json and .env files, install it on an always-on machine like a raspberry pi, let it run with the provided cronjob and let it find all of your favourite media.

### Requirements ### 

## Installation

The system is built and run with Docker to prevent time being wasted on managing dependencies. Simply clone the project and run the `scripts/run-docker-container.sh`, you will need to edit the mountpoint in the script and add your values to `templates/env-template`. 

Currently this project relies on you setting up your own qbittorrent server and entering the details in the `env-template` file, but there is work in progress to create a qbittorrent docker container which would automate that step and use docker-compose to orchestrate the connection. 

## Tests

Tests are located in the `test/` directory, and the unit tests inside the `test/unit_test` directory. Run the tests from the project root directory with this command: `python -m unittest discover -v -s .` after creating and activating a development virtualenv (dependencies are held in `requirements-dev.txt`)

## Licence

This project uses the MIT Licence, found in ./LICENSE

## Disclaimer

This project is not intended to be used for illegal purposes and the consequences of any use of the code in this repository for illegal purposes shall be born solely by the user.

