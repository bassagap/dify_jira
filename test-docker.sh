#!/bin/bash

echo "Testing Docker and Docker Compose availability..."

echo -e "\n1. Checking Docker command:"
if command -v docker &> /dev/null; then
    echo "✅ Docker command found"
    echo "Docker version:"
    docker --version
else
    echo "❌ Docker command not found"
fi

echo -e "\n2. Checking Docker daemon:"
if docker info &> /dev/null; then
    echo "✅ Docker daemon is running"
else
    echo "❌ Docker daemon is not running"
fi

echo -e "\n3. Checking Docker Compose v2:"
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose v2 is available"
    echo "Docker Compose version:"
    docker compose version
else
    echo "❌ Docker Compose v2 is not available"
fi

echo -e "\n4. Checking Docker socket:"
if [ -S /var/run/docker.sock ]; then
    echo "✅ Docker socket exists"
    echo "Docker socket permissions:"
    ls -l /var/run/docker.sock
else
    echo "❌ Docker socket not found"
fi

echo -e "\n5. Checking user groups:"
groups 