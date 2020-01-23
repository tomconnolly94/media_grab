#!/bin/bash

#activate python virtualenv
source venv/bin/activate

#install all dependencies
pip install -r req.txt > /dev/null

#run program
python Main.py