from fastapi import FastAPI, HTTPException, Request
from src.core.jira_rag.jira_client import JiraClient
from typing import Dict, Any, List
import uvicorn
import logging
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import os
from dotenv import load_dotenv
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

# Disable SSL verification warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

def check_env_vars():
    """Check if all required environment variables are set."""
    required_vars = ['JIRA_SERVER_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            logger.error(f"Missing required environment variable: {var}")
    
    if missing_vars:
        env_path = Path('.env')
        if not env_path.exists():
            logger.error(f"No .env file found at {env_path.absolute()}")
            logger.error("Please create a .env file with the following variables:")
            logger.error("JIRA_SERVER_URL=https://your-jira-server.com")
            logger.error("JIRA_EMAIL=your-email@example.com")
            logger.error("JIRA_API_TOKEN=your-api-token")
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Initialize JiraClient with retry logic
def initialize_jira_client(max_retries=3, retry_delay=2):
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Initializing Jira client...")
            client = JiraClient()
            
            # Test the connection by getting server info
            info = client.client.server_info()
            logger.info(f"Successfully connected to Jira server: {info['serverTitle']} (Version: {info['version']})")
            return client
                
        except Exception as e:
            error_msg = str(e)
            if "blocked by our security service" in error_msg:
                logger.warning(f"Attempt {attempt + 1}/{max_retries}: Request blocked by security service. Retrying in {retry_delay} seconds...")
                logger.debug(f"Full error: {error_msg}")
            else:
                logger.error(f"Failed to initialize Jira client: {error_msg}")
                raise
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            
    raise Exception("Failed to initialize Jira client after multiple attempts")

# Load environment variables and initialize Jira client
load_dotenv()
check_env_vars()

try:
    logger.info("Starting Jira client initialization...")
    jira_client = initialize_jira_client()
    logger.info("Jira client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Jira client: {str(e)}")
    jira_client = None

@app.post("/create_test_case")
async def create_test_case(data: Dict[str, Any]):
    """
    Create a test case issue in Jira from Dify chatflow
    
    Expected payload:
    {
        "parent_key": "PROJ-123",  # The issue this test case will be linked to
        "project_key": "PROJ"      # The project where the test case will be created
    }
    """
    if not jira_client:
        raise HTTPException(status_code=503, detail="Jira client not initialized")
    
    try:
        logger.info(f"Creating test case for parent issue {data['parent_key']}")
        
        # Create the test case issue in the specified project
        logger.info(f"Creating test issue in {data['project_key']} project...")
        issue = jira_client.create_test_issue(data["project_key"])
        logger.info(f"Successfully created test issue: {issue.key}")
        logger.info(f"Summary: {issue.summary}")
        logger.info(f"Status: {issue.status}")
        logger.info(f"Description: {issue.description}")
        
        # Link the test case to the parent issue
        jira_client.link_issues(
            inward_key=data["parent_key"],  # The issue this test case is for
            outward_key=issue.key,          # The newly created test case
            link_type="depends on",
            #comment="Test case created via Dify integration"
        )
        
        logger.info(f"Linked test case {issue.key} to parent {data['parent_key']}")
        
        # Get the issue URL
        jira_url = jira_client.server_url.rstrip("/")
        issue_url = f"{jira_url}/browse/{issue.key}"
        
        return {
            "success": True,
            "test_case_key": issue.key,     # The new test case's key (e.g., "PROJ-456")
            "parent_key": data["parent_key"], # The issue this test case is for
            "issue_url": issue_url,
            "summary": issue.summary,
            "status": issue.status,
            "description": issue.description,
            "message": f"Test case {issue.key} created and linked to {data['parent_key']}"
        }
        
    except Exception as e:
        logger.error(f"Error in create_test_case: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_bulk_test_cases")
async def create_bulk_test_cases(data: Dict[str, Any]):
    """
    Create multiple test cases for a parent issue using structured LLM output.
    """
    if not jira_client:
        raise HTTPException(status_code=503, detail="Jira client not initialized")

    try:
        logger.info("Received request to create bulk test cases")
        logger.info(f"Request data: {data}")
        
        parent_key = data["main_issue_key"]
        project_key = parent_key.split('-')[0]
        link_type = data.get("link_type", "Tests")
        labels = data.get("labels", [])
        component = data.get("component")
        reporter = data.get("reporter")

        logger.info(f"Extracted parameters: parent_key={parent_key}, project_key={project_key}, link_type={link_type}")
        logger.info(f"Labels: {labels}, Component: {component}, Reporter: {reporter}")

        results = jira_client.bulk_create_test_issues(
            project_key=project_key,
            test_cases=data["test_cases"],
            parent_key=parent_key,
            link_type=link_type,
            labels=labels,
            component=component,
            reporter=reporter,
        )

        logger.info(f"Bulk creation completed. Results: {results}")
        
        return {
            "success": True,
            "created_cases": results,
            "message": f"Processed {len(results)} test cases for {parent_key}"
        }

    except Exception as e:
        logger.error(f"Error in create_bulk_test_cases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test_jira_connection")
def test_jira_connection():
    if not jira_client:
        return {"success": False, "error": "Jira client not initialized"}
    
    try:
        # Try to get Jira server info
        info = jira_client.client.server_info()
        logger.info(f"Successfully connected to Jira server: {info['serverTitle']} (Version: {info['version']})")
        return {"success": True, "server": info}
    except Exception as e:
        logger.error(f"Error in test_jira_connection: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/get_linked_test_cases/{issue_key}")
def get_linked_test_cases(issue_key: str, link_type: str = "Tests"):
    """
    Retrieve all test cases linked to a given issue.
    """
    if not jira_client:
        raise HTTPException(status_code=503, detail="Jira client not initialized")
    try:
        linked = jira_client.get_linked_issues(issue_key, link_type=link_type)
        # Optionally filter only 'Test' issues
        test_cases = [l for l in linked if l.get("link_type", "").lower() == link_type.lower()]
        return {"success": True, "linked_test_cases": test_cases}
    except Exception as e:
        logger.error(f"Error in get_linked_test_cases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Use a specific IP address that's accessible from WSL
    # You'll need to replace this with your actual Windows IP address
    windows_host = os.getenv("WINDOWS_HOST_IP", "0.0.0.0")
    logger.info(f"Starting API server on host: {windows_host}, port: 8000")
    uvicorn.run("jira_api:app", host=windows_host, port=8000, reload=True) 