#!/bin/bash
export HOSTNAME=$(hostname)
# Launching using the --file and --project-directory flags
docker compose -f ./Frigate-Viewer/docker-compose.yaml --project-directory ./Frigate-Viewer up -d
export HOSTNAME=$(hostname)
docker compose -f ./Watcher-Scripts/docker-compose.yaml --env-file ./Watcher-Scripts/.env --project-directory ./Watcher-Scripts up -d

echo "Services launched."
