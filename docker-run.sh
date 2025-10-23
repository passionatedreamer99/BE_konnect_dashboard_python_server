#!/bin/bash

# Docker run script for Konnect Service
# This script helps you run the Konnect service using Docker

echo "Starting Konnect Service with Docker..."

# Build the Docker image
echo "Building Docker image..."
docker build -t konnect-service .

# Run the container
echo "Starting container..."
docker run -d \
  --name konnect-container \
  -p 5004:5004 \
  -v $(pwd)/konnect_db.sqlite:/app/konnect_db.sqlite \
  konnect-service

echo "Konnect service is running on http://localhost:5004"
echo "Health check: http://localhost:5004/health"
echo ""
echo "To stop the container: docker stop konnect-container"
echo "To remove the container: docker rm konnect-container"
echo "To view logs: docker logs konnect-container"
