#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up Dify project...${NC}"

# Function to check required tools
check_requirements() {
    echo -e "${YELLOW}Checking requirements...${NC}"
    
    # Check for git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}git is not installed. Please install git first.${NC}"
        exit 1
    fi
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
    
    # Check for Docker Compose
    if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}All requirements are satisfied!${NC}"
}

# Function to setup Dify submodule
setup_dify_submodule() {
    echo -e "${YELLOW}Setting up Dify submodule...${NC}"
    
    # Check if .gitmodules exists
    if [ ! -f .gitmodules ]; then
        echo -e "${YELLOW}Creating .gitmodules file...${NC}"
        echo "[submodule \"dify\"]
    path = dify
    url = https://github.com/langgenius/dify.git
    branch = main" > .gitmodules
    fi

    # Check if dify directory exists
    if [ -d "dify" ]; then
        echo -e "${YELLOW}Removing existing dify directory...${NC}"
        rm -rf dify
    fi

    echo -e "${YELLOW}Cloning Dify repository...${NC}"
    git clone https://github.com/langgenius/dify.git dify
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to clone Dify repository. Please check your git configuration and try again.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Successfully set up Dify repository!${NC}"
}

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        echo -e "${YELLOW}Initializing git repository...${NC}"
        git init
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to initialize git repository. Please check your git configuration and try again.${NC}"
            exit 1
        fi
        echo -e "${GREEN}Successfully initialized git repository!${NC}"
    fi
}

# Function to check Docker status and wait for it to be ready
check_docker() {
    echo -e "${YELLOW}Checking Docker status...${NC}"
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker info &> /dev/null; then
            echo -e "${GREEN}Docker is running and accessible!${NC}"
            return 0
        fi
        echo -e "${YELLOW}Waiting for Docker to be ready (attempt $attempt/$max_attempts)...${NC}"
        sleep 2
        attempt=$((attempt + 1))
    done

    echo -e "${RED}Docker is not running or not accessible after $max_attempts attempts.${NC}"
    if [ -n "$CODESPACES" ]; then
        echo -e "${YELLOW}You are in Codespaces. Please ensure:${NC}"
        echo -e "1. The devcontainer.json has Docker feature enabled"
        echo -e "2. The container has been rebuilt with Docker support"
        echo -e "3. You have sufficient permissions"
        echo -e "4. Try rebuilding the container"
    else
        echo -e "${YELLOW}Please ensure Docker is installed and running.${NC}"
    fi
    exit 1
}

# Function to start Docker containers
start_containers() {
    local compose_file="docker-compose.yml"
    echo -e "${YELLOW}Starting Docker containers using $compose_file...${NC}"

    # Check if compose file exists
    if [ ! -f "$compose_file" ]; then
        echo -e "${RED}Docker Compose file not found: $compose_file${NC}"
        return 1
    fi

    # Try docker compose v2 first
    if docker compose version &> /dev/null; then
        echo -e "${YELLOW}Using Docker Compose V2...${NC}"
        docker compose -f "$compose_file" up -d
        if [ $? -eq 0 ]; then
            return 0
        fi
    fi

    # Try docker-compose v1 as fallback
    if command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}Using Docker Compose V1...${NC}"
        docker-compose -f "$compose_file" up -d
        if [ $? -eq 0 ]; then
            return 0
        fi
    fi

    echo -e "${RED}Failed to start containers. Neither docker compose v2 nor docker-compose v1 is available.${NC}"
    return 1
}

# Check requirements first
check_requirements

# Check if we're in a git repository
check_git_repo

# Setup Dify submodule
setup_dify_submodule

# Navigate to Dify docker directory
echo -e "${YELLOW}Setting up Dify environment...${NC}"
cd dify/docker || {
    echo -e "${RED}Failed to navigate to dify/docker directory${NC}"
    exit 1
}

# Copy environment configuration file
echo -e "${YELLOW}Copying environment configuration...${NC}"
if [ -f ".env.example" ]; then
    cp .env.example .env
    echo -e "${GREEN}Environment configuration copied successfully!${NC}"
else
    echo -e "${RED}Failed to find .env.example file${NC}"
    exit 1
fi

# Check Docker status and wait for it to be ready
check_docker

# Start Docker containers
if ! start_containers; then
    echo -e "${RED}Failed to start containers. Please check the error messages above.${NC}"
    exit 1
fi

# Check if containers are running
echo -e "${YELLOW}Checking container status...${NC}"
if docker compose version &> /dev/null; then
    docker compose -f docker-compose.yml ps
else
    docker-compose -f docker-compose.yml ps
fi

echo -e "${GREEN}Dify setup completed!${NC}"
echo -e "${YELLOW}Next steps:${NC}"

# Adjust URLs based on environment
if [ -n "$CODESPACES" ]; then
    echo -e "1. Access the administrator initialization page at: ${GREEN}https://$CODESPACE_NAME-80.preview.app.github.dev/install${NC}"
    echo -e "2. Set up your admin account"
    echo -e "3. Access the Dify web interface at: ${GREEN}https://$CODESPACE_NAME-80.preview.app.github.dev${NC}"
    echo -e "${YELLOW}Note: If you encounter network issues, you may need to:${NC}"
    echo -e "   - Configure your Codespace to use a proxy"
    echo -e "   - Add necessary environment variables to your .env file"
    echo -e "   - Check the Docker container logs for any network-related errors"
else
    echo -e "1. Access the administrator initialization page at: ${GREEN}http://localhost/install${NC}"
    echo -e "2. Set up your admin account"
    echo -e "3. Access the Dify web interface at: ${GREEN}http://localhost${NC}"
fi

echo -e "${YELLOW}Note: Make sure Docker is running and has sufficient resources allocated.${NC}" 