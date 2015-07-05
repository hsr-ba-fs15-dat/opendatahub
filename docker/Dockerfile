FROM ubuntu:14.04.1

MAINTAINER Fabio Scala <fabio.scala@gmail.com>

EXPOSE 80

RUN mkdir /opendatahub

WORKDIR /opendatahub

RUN apt-get update && \
	apt-get install -y git vim python-pip python-virtualenv python-dev phantomjs gdal-bin libgdal-dev libgdal1h libgdal1-dev libfreetype6 libfreetype6-dev libxml2-dev libxslt-dev python-dev openjdk-7-jre nodejs nodejs-legacy npm && \
	npm install -g npm@latest && \
	npm install -g bower grunt-cli less typescript tsd@next

RUN git clone https://github.com/hsr-ba-fs15-dat/opendatahub.git . && \
	make env

RUN . ~/env/bin/activate && \
	export DJANGO_CONFIG=PRODUCTION && \
	pyb -v django_collectstatic

ENV DATABASE_URL=postgres://postgres:@db:5432/postgres \
	DJANGO_CONFIG=PRODUCTION \
	DJANGO_ALLOWED_HOSTS=* \
	GITHUB_SECRET=a827b6121fc4fbb85f8c09c4276b64377b150ddf

CMD . ~/env/bin/activate && \
	pyb -v django_makemigrations django_migrate && \
	gunicorn -b 0.0.0.0:80 --pythonpath src/main/python opendatahub.wsgi
