Media Grab Webapp
========

### The Idea ###

This project is designed to be a simple framework frontend for the [media_grab](https://github.com/tomconnolly94/media_grab) system. It is a Vue.js web app with a python flask backend that facilitates edits to the mediaIndex.json file which is the single source of truth for media download targets.

## Installation

The system is built and run with Docker to prevent time being wasted on managing dependencies. Simply clone the project and run `docker-compose up --build` from the project's root directory.

## Tests

Backend tests are located in the `flask-container/server/test/` directory, and the unit tests inside the `test/unit_test` directory. Run the tests from the `flask-container/server` directory with this command: `python -m unittest discover -v -s .` after creating and activating a development virtualenv (dependencies are held in `flask-container/requirements-dev.txt`)

## Licence

This project uses the MIT Licence, found in ./LICENSE

## Disclaimer

This project is not intended to be used for illegal purposes and the consequences of any use of the code in this repository for illegal purposes shall be born solely by the user.

## Issues

Please report issues via github, I will try to respond quickly