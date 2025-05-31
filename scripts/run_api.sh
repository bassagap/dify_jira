#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Jira-Dify Integration API...${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create a .env file with the required environment variables:${NC}"
    echo -e "JIRA_SERVER_URL=https://your-jira-server.com"
    echo -e "JIRA_EMAIL=your-email@example.com"
    echo -e "JIRA_API_TOKEN=your-api-token"
    echo -e "DIFY_BASE_URL=http://localhost/v1"
    echo -e "DIFY_DATASET_API_KEY=your-dify-api-key"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Set PYTHONPATH to include the src directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Start the API server
echo -e "${YELLOW}Starting API server...${NC}"
echo -e "${GREEN}API will be available at:${NC}"
echo -e "  - Main API: http://localhost:8000"
echo -e "  - Swagger UI: http://localhost:8000/docs"
echo -e "  - ReDoc: http://localhost:8000/redoc"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"

uvicorn src.api.jira_api:app --host 0.0.0.0 --port 8000 --reload 