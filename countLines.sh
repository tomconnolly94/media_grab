#!/bin/bash

find . -path ./venv -prune -false -o  -name "*.py" -print0 | xargs -0 wc -l
