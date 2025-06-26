#!/bin/bash

echo "Stopping all services..."
docker-compose down

echo "Services stopped."
echo "To remove all data volumes as well, run: docker-compose down -v" 