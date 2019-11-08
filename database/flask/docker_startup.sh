#!/bin/bash

docker stop bflabs
docker rm bflabs
docker build -t bflabs_flask .
docker run --add-host="postgreshost:172.17.0.1" -d -p 5005:5005 --restart=always --name bflabs bflabs_flask
