#!/bin/bash

# Build the Docker image with verbose progress
BUILDKIT_PROGRESS=plain docker build -t squidnet .

# Ensure permissions for host directories are set for all users
chmod -R 777 "$(pwd)/payload"
chmod -R 777 "$(pwd)/output"

# Run the container with bind mounts
docker run \
  --mount type=bind,source="$(pwd)/payload",target=/app/payload \
  --mount type=bind,source="$(pwd)/output",target=/app/output \
  -it --network host squidnet