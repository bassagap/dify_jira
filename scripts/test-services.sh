#!/bin/bash

echo "Testing all services..."
echo "======================"

# Function to test a service
test_service() {
    local name=$1
    local url=$2
    local endpoint=$3
    
    echo "Testing $name..."
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url$endpoint")
    
    if [ "$response" = "200" ]; then
        echo "✅ $name is working (HTTP $response)"
    else
        echo "❌ $name is not responding properly (HTTP $response)"
    fi
    echo ""
}

# Wait a bit for services to start
echo "Waiting for services to start up..."
sleep 10

# Test Jira API
test_service "Jira API" "http://localhost:8000" "/test_jira_connection"

# Test Student API
test_service "Student API" "http://localhost:8001" "/test_connection"

# Test Dify API
test_service "Dify API" "http://localhost:5001" "/health"

# Test Dify Web
test_service "Dify Web" "http://localhost:3000" "/"

# Test Weaviate
test_service "Weaviate" "http://localhost:8080" "/v1/.well-known/ready"

echo "======================"
echo "Service URLs:"
echo "- Jira API: http://localhost:8000"
echo "- Student API: http://localhost:8001"
echo "- Dify Web: http://localhost:3000"
echo "- Dify API: http://localhost:5001"
echo "- Weaviate: http://localhost:8080"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down" 