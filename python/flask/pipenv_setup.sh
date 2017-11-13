#!/bin/bash

# pin pipenv version, issues install flask at ~8.3
pip install pipenv==8.2.7
pip install wheel

# setup pipenv
pipenv install -e . --dev --python $(cat .python-version)

