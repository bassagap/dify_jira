#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[1;36m'
MAGENTA='\033[1;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Simple Testus Patronus Banner with a magical owl
cat << "EOF"
${MAGENTA}                                                
        ,_,        
      (O,O)   Testus Patronus: Jira Ingestion Magic!
      (   )        
       \" \"         
${NC}
EOF

# Script start

echo -e "${YELLOW}Starting Jira-Dify Integration API...${NC}"

# Look for .env in root or config directory
if [ -f ".env" ]; then
    ENV_PATH=".env"
elif [ -f "../.env" ]; then
    ENV_PATH="../.env"
elif [ -f "../config/.env" ]; then
    ENV_PATH="../config/.env"
elif [ -f "config/.env" ]; then
    ENV_PATH="config/.env"
else
    echo -e "${RED}Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create a .env file with the required environment variables:${NC}"
    echo -e "JIRA_SERVER_URL=https://your-jira-server.com"
    echo -e "JIRA_EMAIL=your-email@example.com"
    echo -e "JIRA_API_TOKEN=your-api-token"
    echo -e "DIFY_BASE_URL=http://localhost/v1"
    echo -e "DIFY_DATASET_API_KEY=your-dify-api-key"
    exit 1
fi

# Export environment variables
set -a
source "$ENV_PATH"
set +a

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Set PYTHONPATH to the project root
export PYTHONPATH=$PYTHONPATH:$(cd .. && pwd)

# Codespaces Swagger UI block
if [ -n "$CODESPACE_NAME" ]; then
    SWAGGER_URL="https://${CODESPACE_NAME}-8000.app.github.dev/docs"
    echo -e "\n${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${MAGENTA}🪄  MAGIC PORTAL TO YOUR API DOCS!  🪄${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${GREEN}👉 You MUST open the Swagger UI in your browser to use the API:${NC}"
    echo -e "${BOLD}${MAGENTA}$SWAGGER_URL${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${YELLOW}✨ Click or Ctrl+Click the link above to open the magical API documentation! ✨${NC}\n"
fi

echo -e "${YELLOW}Starting API server...${NC}"
echo -e "${GREEN}API will be available at:${NC}"
echo -e "  - Main API: http://localhost:8000"
echo -e "  - Swagger UI: http://localhost:8000/docs"
echo -e "  - ReDoc: http://localhost:8000/redoc"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"

uvicorn src.api.student_api:app --host 0.0.0.0 --port 8000 --reload 