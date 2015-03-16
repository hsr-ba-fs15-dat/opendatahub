# OpenDataHub
[![Build Status](https://travis-ci.org/hsr-ba-fs15-dat/opendatahub.svg?branch=master)](https://travis-ci.org/hsr-ba-fs15-dat/opendatahub)

HSR OpenDataHub Webapplication

## Latest build
[opendatahub-hsr-dev on Heroku](https://opendatahub-hsr-dev.herokuapp.com/)

## Developer FAQ

### How to drop all tables

1. Delete all migrations (*.py) in the individual django app folders/migrations
2. `./manage.p dbshell`
3. `SELECT 'DROP TABLE ' || tablename || ' CASCADE;' FROM pg_tables WHERE tableowner = 'opendatahub';`
4. Paste output