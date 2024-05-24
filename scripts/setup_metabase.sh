#!/bin/bash

echo "Setting up dashboard environment..."

docker-compose up -d

echo "Dashboard setup complete. Metabase on port 3000, Superset on port 8088, Redash on port 5000."
