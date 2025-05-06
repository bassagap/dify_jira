FROM langgenius/dify-api:latest

# Install development tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install Python development tools
RUN pip install --no-cache-dir \
    black \
    pylint \
    pytest \
    pytest-cov

# Set up workspace
WORKDIR /workspace

# Copy requirements file
COPY requirements.txt /workspace/

# Install project dependencies
RUN pip install -r requirements.txt 