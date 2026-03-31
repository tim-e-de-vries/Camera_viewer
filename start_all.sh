#!/bin/bash
export HOSTNAME=$(hostname)
# Launching using the --file and --project-directory flags
docker compose -f ./Frigate-Viewer/docker-compose.yaml --project-directory ./Frigate-Viewer up -d
#docker compose -f ./MQTT/docker-compose.yaml --project-directory ./MQTT up -d
docker compose -f ./Watcher-Scripts/docker-compose.yaml --project-directory ./Watcher-Scripts up -d

echo "Services launched."
