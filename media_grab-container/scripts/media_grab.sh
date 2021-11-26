#!/bin/bash

#move to project directory
cd $(dirname "$0")

#activate python virtualenv
source venv/bin/activate

#install all dependencies
pip install -r req.txt > /dev/null

#run program
python Main.py