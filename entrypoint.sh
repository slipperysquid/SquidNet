#!/bin/bash

# Ensure the container user has ownership of mounted directories
chown -R builderbob:builderbob /app/payload /app/output

# Execute the container's CMD
exec "$@"
