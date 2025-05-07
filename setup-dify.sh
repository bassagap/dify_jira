#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up Dify project...${NC}"


# Initialize and update submodules
echo -e "${YELLOW}Initializing Dify submodule...${NC}"
if git submodule update --init --recursive; then
    echo -e "${GREEN}Successfully initialized Dify submodule!${NC}"
else
    echo -e "${RED}Failed to initialize Dify submodule. Please check your git configuration and try again.${NC}"
    exit 1
fi

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
    sudo systemctl restart docker
fi

# Start Docker containers
echo -e "${YELLOW}Starting Docker containers...${NC}"
if command -v docker-compose &> /dev/null; then
    # Using docker-compose v1
    docker-compose up -d
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    # Using docker compose v2
    docker compose up -d
else
    echo -e "${RED}Neither docker-compose nor docker compose is available. Please install Docker and Docker Compose first.${NC}"
    exit 1
fi

# Check if containers are running
echo -e "${YELLOW}Checking container status...${NC}"
if command -v docker-compose &> /dev/null; then
    docker-compose ps
else
    docker compose ps
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