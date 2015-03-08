#!/bin/bash

cd "$(dirname "$0")"/..

virtualenv ~/env
source ~/env/bin/activate
pip install pybuilder
pyb install_dependencies


cd src/main/webapp/

# Install deps
npm install
bower install --config.analytics=false --allow-root

# Compile SASS
grunt compass
