#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up Dify project...${NC}"

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

    # Check if dify directory exists and is empty
    if [ ! -d "dify" ] || [ -z "$(ls -A dify 2>/dev/null)" ]; then
        echo -e "${YELLOW}Initializing Dify submodule...${NC}"
        # Remove existing dify directory if it exists but is empty
        [ -d "dify" ] && rm -rf dify
        
        # Initialize and update submodule
        git submodule add https://github.com/langgenius/dify.git dify
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to add Dify submodule. Please check your git configuration and try again.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Updating existing Dify submodule...${NC}"
        git submodule update --init --recursive
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to update Dify submodule. Please check your git configuration and try again.${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}Successfully set up Dify submodule!${NC}"
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

# Configure proxy settings for Docker if in Codespaces
if [ -n "$CODESPACES" ]; then
    echo -e "${YELLOW}Configuring Docker proxy settings...${NC}"
    # Create or update Docker daemon configuration
    sudo mkdir -p /etc/docker
    echo '{
        "proxies": {
            "default": {
                "httpProxy": "http://proxy:3128",
                "httpsProxy": "http://proxy:3128",
                "noProxy": "localhost,127.0.0.1"
            }
        }
    }' | sudo tee /etc/docker/daemon.json > /dev/null
    
    # Restart Docker daemon to apply proxy settings
    if command -v systemctl &> /dev/null; then
        sudo systemctl restart docker
    else
        # Alternative restart method for environments without systemctl
        sudo service docker restart
    fi
fi

# Start Docker containers
echo -e "${YELLOW}Starting Docker containers...${NC}"
if docker compose version &> /dev/null; then
    # Using docker compose v2
    docker compose up -d
elif command -v docker-compose &> /dev/null; then
    # Using docker-compose v1
    docker-compose up -d
else
    echo -e "${RED}Failed to start containers. Please try running the script again.${NC}"
    exit 1
fi

# Check if containers are running
echo -e "${YELLOW}Checking container status...${NC}"
if docker compose version &> /dev/null; then
    docker compose ps
else
    docker-compose ps
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