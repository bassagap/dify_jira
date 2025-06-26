FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src/
COPY .env .

# Expose ports
EXPOSE 8000 8001

# Create a startup script to run both services
RUN echo '#!/bin/bash\n\
echo "Starting Jira API on port 8000..."\n\
uvicorn src.api.jira_api:app --host 0.0.0.0 --port 8000 &\n\
echo "Starting Student API on port 8001..."\n\
uvicorn src.api.student_api:app --host 0.0.0.0 --port 8001 &\n\
wait' > /app/start.sh && chmod +x /app/start.sh

# Command to run both applications
CMD ["/app/start.sh"] 