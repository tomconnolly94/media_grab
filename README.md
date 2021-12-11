Media Grab
========

### The Idea ###

This project is designed to automate the download and organisation of media. It can be time-consuming to search for, download and manage your media, this project combats that waste of time by promoting automation. Use the webapp to load up your favourite TV shows and watch them download automatically preventing you ever having to search for a show again.

## Installation

This multi container system is built and run with Docker and docker compose and is configured using an env file. A template for this .env can be found at ./env-template. Simply run:
```
cp ./env-template ./.env
```

to create your own env file.


## Tests

Tests are located in the `test/` directory, and the unit tests inside the `test/unit_test` directory. Run the tests from the project root directory with this command: `python -m unittest discover -v -s .` after creating and activating a development virtualenv (dependencies are held in `requirements-dev.txt`)

## Licence

This project uses the MIT Licence, found in ./LICENSE

## Disclaimer

This project is not intended to be used for illegal purposes and the consequences of any use of the code in this repository for illegal purposes shall be born solely by the user.
