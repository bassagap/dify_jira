from fastapi import FastAPI, HTTPException, Query
from src.core.models.ingest_models import IngestJiraRequest, IngestJsonRequest
from src.core.jira_rag.jira_client import JiraClient
from src.core.jira_rag.dify_integration import DifyIntegration, DifyConfigurationError
from typing import Optional, List
import os
from dotenv import load_dotenv
import logging
from pathlib import Path
import requests
import json
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Student Jira-Dify Ingestion API",
    description="API for students to ingest Jira issues from Jira or JSON files, and test connections.",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    load_dotenv()
    logger.info("Environment variables loaded.")

@app.post("/ingest/jira")
def ingest_from_jira(request: IngestJiraRequest, advanced_ingestion: bool = Query(False, description="Enable advanced ingestion (aliases and queries)?")):
    """
    Ingest issues from Jira into Dify. Provide either a JQL query or a project key.
    """
    try:
        jira_client = JiraClient()
        dify = DifyIntegration(advanced_ingestion=advanced_ingestion)
        if request.jql:
            jql_query = request.jql
        elif request.project:
            jql_query = f"project = {request.project} ORDER BY created DESC"
        else:
            raise HTTPException(status_code=400, detail="You must provide either a 'jql' or 'project' parameter.")
        issues = jira_client.get_issues(jql_query, max_results=request.max_results)
        if not issues:
            return {"success": False, "message": "No issues found for the given query."}
        dify.ingest_issues(issues, advanced_ingestion=advanced_ingestion)
        return {"success": True, "message": f"Ingested {len(issues)} issues from Jira."}
    except Exception as e:
        logger.error(f"Error ingesting from Jira: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest/json")
def ingest_from_json(request: IngestJsonRequest, advanced_ingestion: bool = Query(False, description="Enable advanced ingestion (aliases and queries)?")):
    """
    Ingest issues from a list of JSON files in the dataset directory into Dify.
    All documents will be ingested into the same dataset.
    """
    results = []
    errors = []
    try:
        dify = DifyIntegration(advanced_ingestion=advanced_ingestion)
        dataset_dir = Path(request.dataset_dir)
        for file_name in request.file_names:
            try:
                logger.info(f"Starting JSON ingestion for file: {file_name} in directory: {request.dataset_dir}")
                file_path = dataset_dir / file_name

                logger.info(f"Checking if file exists at path: {file_path}")
                if not file_path.exists():
                    error_msg = f"File not found: {file_path}"
                    logger.error(error_msg)
                    errors.append({"file": file_name, "error": error_msg})
                    continue

                logger.info(f"File found. Attempting to ingest JSON file: {file_path}")
                try:
                    result = dify.ingest_json_file(str(file_path), advanced_ingestion=advanced_ingestion)
                    logger.info(f"Successfully ingested JSON file. Result: {result}")
                    results.append({"file": file_name, "result": result})
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON format in file {file_path}: {str(e)}"
                    logger.error(error_msg)
                    errors.append({"file": file_name, "error": error_msg})
                except Exception as e:
                    error_msg = f"Error during Dify ingestion: {str(e)}"
                    logger.error(f"{error_msg}\n{traceback.format_exc()}")
                    errors.append({"file": file_name, "error": error_msg})
            except Exception as e:
                error_msg = f"Unexpected error during JSON ingestion for file {file_name}: {str(e)}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                errors.append({"file": file_name, "error": error_msg})
        return {"success": len(errors) == 0, "results": results, "errors": errors}
    except DifyConfigurationError as e:
        logger.error(f"Dify configuration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error ingesting from JSON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test_connection")
def test_connection():
    """
    Test connection to Jira and Dify.
    """
    results = {"jira": False, "dify": False, "errors": {}}
    try:
        jira_client = JiraClient()
        info = jira_client.client.server_info()
        results["jira"] = True
        results["jira_info"] = info
    except Exception as e:
        results["errors"]["jira"] = str(e)
    try:
        dify = DifyIntegration()
        # Try to list datasets as a simple check
        url = f"{dify.base_url}/datasets"
        resp = dify.headers
        r = requests.get(url, headers=dify.headers)
        r.raise_for_status()
        results["dify"] = True
    except Exception as e:
        results["errors"]["dify"] = str(e)
    return results 