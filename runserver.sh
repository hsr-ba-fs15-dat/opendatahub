#!/bin/bash

cd "$(dirname "$0")"/src/main/python
python ./manage.py runserver_plus 0.0.0.0:5000
