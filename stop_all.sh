
#!/bin/bash

# Launching using the --file and --project-directory flags
docker compose -f ./Frigate-Viewer/docker-compose.yaml --project-directory ./Frigate-Viewer down
#docker compose -f ./MQTT/docker-compose.yaml --project-directory ./MQTT down
docker compose -f ./Watcher-Scripts/docker-compose.yaml --project-directory ./Watcher-Scripts down
#docker rm frigate-listener
echo "Services unlaunched."
