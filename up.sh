#!/bin/bash
set -e

IMAGE="python:3.11-slim"

# Check if the image already exists locally
if ! docker image inspect $IMAGE > /dev/null 2>&1; then
  docker pull $IMAGE
fi

docker compose up -d --build
