#!/bin/bash

# Start all services with docker-compose
echo "Starting all services..."
echo "This will start:"
echo "- Jira API (port 8000)"
echo "- Student API (port 8001)"
echo "- Dify Web (port 3000)"
echo "- Dify API (port 5001)"
echo "- PostgreSQL (internal)"
echo "- Redis (internal)"
echo "- Weaviate (port 8080)"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file with the following variables:"
    echo "JIRA_SERVER_URL=your-jira-server-url"
    echo "JIRA_EMAIL=your-email"
    echo "JIRA_API_TOKEN=your-api-token"
    echo "DIFY_API_KEY=your-dify-api-key"
    echo "DIFY_BASE_URL=your-dify-base-url"
    exit 1
fi

# Start the services
docker-compose up -d

echo ""
echo "Services are starting up..."
echo "You can check the status with: docker-compose ps"
echo "View logs with: docker-compose logs -f"
echo ""
echo "Once all services are healthy, you can access:"
echo "- Jira API: http://localhost:8000"
echo "- Student API: http://localhost:8001"
echo "- Dify Web: http://localhost:3000"
echo "- Dify API: http://localhost:5001"
echo "- Weaviate: http://localhost:8080" 