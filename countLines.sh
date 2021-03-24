#!/bin/bash

find . -type d \( -path ./venv -o -path ./venv-dev \) -prune -false -o  -name "*.py" -print0 | xargs -0 wc -l
