#!/bin/bash

echo "WARNING: This script will remove stopped containers, unused images, networks, volumes, and build cache."
echo "Make sure you understand the consequences before proceeding."
read -r -p "Are you sure you want to continue? [y/N] " response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
  echo "Pruning containers..."
  docker container prune -f

  echo "Pruning images..."
  docker image prune -a -f

  echo "Pruning volumes..."
  docker volume prune -f

  echo "Pruning networks..."
  docker network prune -f
  
  echo "Pruning build cache..."
  docker builder prune -a -f

  echo "Cleanup complete."
else
  echo "Cleanup aborted."
fi
