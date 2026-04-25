#!/bin/bash

# Security and Clean Code: Fail fast. Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting Deployment Process..."

# 1. Update repository
echo "Pulling latest changes from master branch..."
git pull origin master

# 2. Rebuild and restart Docker containers cleanly
echo "Rebuilding Docker containers..."
docker compose up -d --build

# 3. Clean up dangling images to save EC2 disk space
echo "Cleaning up old Docker images..."
docker image prune -f

echo "Deployment completed successfully!"