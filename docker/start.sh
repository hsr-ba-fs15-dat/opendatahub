#!/bin/bash

docker run --name opendatahub_db -d postgres:9.3
docker run -ti -p 80:80 --link opendatahub_db:db fabioscala/opendatahub:ba
