#!/bin/bash

# This script will use Docker Compose to build and start the containers
# with the specified environment file and options.

# Ensure script is executable: chmod +x run.sh
# Run the script: ./run.sh

docker-compose --env-file docker.env up --build --force-recreate -d
