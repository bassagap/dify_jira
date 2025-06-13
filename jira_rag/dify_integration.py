from typing import List, Dict
import requests
import os
from dotenv import load_dotenv
from .jira_client import JiraIssue
import uuid 
import json
from pathlib import Path
import re
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

class DifyIntegration:
    def __init__(self, api_key: str = None, base_url: str = None, dataset_id: str = None, project_key: str = None):
        load_dotenv()
        
        self.dataset_api_key = api_key or os.getenv('DIFY_DATASET_API_KEY')
        self.base_url = base_url or os.getenv('DIFY_BASE_URL', 'http://localhost/v1')
        self.dataset_id = dataset_id or os.getenv('DIFY_DATASET_ID')
        self.project_key = project_key or os.getenv('JIRA_PROJECT_KEY', 'DEFAULT')
        
        if not self.dataset_api_key:
            raise ValueError("Missing Dify API key. Please provide it or set DIFY_DATASET_API_KEY environment variable.")
        self.headers = {
            'Authorization': f'Bearer {self.dataset_api_key}',
            'Content-Type': 'application/json'
        }
        if not self.dataset_id:
             self.dataset_id = self.create_dataset()
        
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Normalize case (optional)
        # text = text.lower()
        
        return text.strip()

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date format"""
        try:
            # Parse the date
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Convert to a standard format
            return date_obj.strftime('%Y-%m-%d %H:%M:%S %Z')
        except Exception as e:
            logger.warning(f"Failed to normalize date {date_str}: {str(e)}")
            return date_str

    def _normalize_status(self, status: str) -> str:
        """Normalize status values"""
        status_map = {
            'in progress': 'In Progress',
            'in-progress': 'In Progress',
            'in_progress': 'In Progress',
            'to do': 'To Do',
            'todo': 'To Do',
            'done': 'Done',
            'closed': 'Closed',
            'open': 'Open',
            'blocked': 'Blocked',
            'in review': 'In Review',
            'in_review': 'In Review',
            'in-review': 'In Review'
        }
        return status_map.get(status.lower(), status)

    def _normalize_issue_type(self, issue_type: str) -> str:
        """Normalize issue type values"""
        type_map = {
            'bug': 'Bug',
            'task': 'Task',
            'story': 'Story',
            'epic': 'Epic',
            'subtask': 'Subtask',
            'test': 'Test',
            'feature': 'Feature',
            'improvement': 'Improvement'
        }
        return type_map.get(issue_type.lower(), issue_type)

    def _validate_issue_data(self, issue: Dict) -> bool:
        """Validate issue data before ingestion"""
        required_fields = ['key', 'summary', 'description', 'status']
        if isinstance(issue, JiraIssue):
            return all(hasattr(issue, field) for field in required_fields)
        else:
            return all(field in issue.get('fields', {}) for field in required_fields)

    def _format_issue_for_text(self, issue: Dict) -> Dict:
        """Format a Jira issue into a document suitable for Dify ingestion with proper cleaning"""
        # Validate issue data
        if not self._validate_issue_data(issue):
            logger.error(f"Invalid issue data: {issue}")
            raise ValueError("Invalid issue data: missing required fields")

        # Handle both JiraIssue objects and dictionary issues
        if isinstance(issue, JiraIssue):
            key = issue.key
            project = issue.project
            issue_type = self._normalize_issue_type(issue.issue_type)
            status = self._normalize_status(issue.status)
            assignee = issue.assignee or 'Unassigned'
            created = self._normalize_date(issue.created)
            updated = self._normalize_date(issue.updated)
            summary = self._clean_text(issue.summary)
            description = self._clean_text(issue.description or 'No description provided')
        else:
            key = issue['key']
            project = issue['fields']['project']['key']
            issue_type = self._normalize_issue_type(issue['fields']['issuetype']['name'])
            status = self._normalize_status(issue['fields']['status']['name'])
            assignee = issue['fields'].get('assignee', {}).get('name', 'Unassigned')
            created = self._normalize_date(issue['fields']['created'])
            updated = self._normalize_date(issue['fields']['updated'])
            summary = self._clean_text(issue['fields']['summary'])
            description = self._clean_text(issue['fields'].get('description', 'No description provided'))

        # Log the cleaning process
        logger.info(f"Cleaned and normalized issue {key}")
        logger.debug(f"Original summary: {issue.summary if isinstance(issue, JiraIssue) else issue['fields']['summary']}")
        logger.debug(f"Cleaned summary: {summary}")

        return {
            "name": f"Jira Issue {key}",
            "text": f"""
                Jira Issue: {key}
                Project: {project}
                Type: {issue_type}
                Status: {status}
                Assignee: {assignee}
                Created: {created}
                Updated: {updated}
                \nSummary: {summary}\n\nDescription:\n{description}
            """,
            "indexing_technique": "economy",
            "process_rule": {"mode": "automatic"}
        }
    
    def _format_issue_metadata(self, issue: Dict, document_id: str, metadata_id:str):
        # Handle both JiraIssue objects and dictionary issues
        issue_key = issue.key if isinstance(issue, JiraIssue) else issue['key']
        return {"operation_data": [{"document_id": document_id, "metadata_list":[{"id": metadata_id, "value": issue_key, "name": "issue_key"}]}]}
    
    def _enable_builtin_metadata(self):
        url = f"{self.base_url}/datasets/{self.dataset_id}/metadata/built-in/enable"
        return requests.post(url, headers=self.headers)
    
        
    def _create_knowledge_metadata(self):
        url = f"{self.base_url}/datasets/{self.dataset_id}/metadata"
        metadata= {"type": "string", "name": "issue_key"}
        return requests.post(url, headers=self.headers, json = metadata)
        
    def ingest_issues(self, issues: List[Dict]) -> List[Dict]:
        """
        Ingest Jira issues into Dify Knowledge Base (Dataset) as documents
        Args:
            issues: List of JiraIssue objects or dictionaries to ingest
        Returns:
            List of responses from Dify API
        """
        responses = []
        self._enable_builtin_metadata()
        metadata_id = self._create_knowledge_metadata().json()["id"]
        for issue in issues:
            url = f"{self.base_url}/datasets/{self.dataset_id}/document/create-by-text"
            
            data = self._format_issue_for_text(issue)
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            responses.append(response.json())
            
            metadata = self._format_issue_metadata(issue=issue, document_id=response.json()["document"]["id"], metadata_id = metadata_id)
            url_metadata = f"{self.base_url}/datasets/{self.dataset_id}/documents/metadata"
            response = requests.post(url_metadata, headers=self.headers, json=metadata)
            responses.append(response.json())

        return responses

    def ingest_json_file(self, json_file_path: str) -> List[Dict]:
        """
        Ingest issues from a JSON file into Dify Knowledge Base
        Args:
            json_file_path: Path to the JSON file containing Jira issues
        Returns:
            List of responses from Dify API
        """
        try:
            with open(json_file_path, 'r') as f:
                issues = json.load(f)
            return self.ingest_issues(issues)
        except Exception as e:
            raise Exception(f"Error ingesting JSON file {json_file_path}: {str(e)}")

    def delete_documents(self, document_ids: List[str]) -> Dict:
        """
        Delete documents from Dify RAG (if supported by your Dify version)
        Args:
            document_ids: List of document IDs to delete
        Returns:
            Response from Dify API
        """
        # This endpoint may need to be updated for knowledge base documents
        response = requests.delete(
            f"{self.base_url}/documents",
            headers=self.headers,
            json={"document_ids": document_ids}
        )
        response.raise_for_status()
        return response.json()

    def _generate_dataset_name(self) -> str:
        """Generate a meaningful dataset name based on project and timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"jira_{self.project_key}_{timestamp}"

    def create_dataset(self, permission: str = "only_me") -> str:
        """
        Create a new dataset with a meaningful name
        Args:
            permission: Dataset permission level
        Returns:
            Dataset ID
        """
        dataset_name = self._generate_dataset_name()
        url = f"{self.base_url}/datasets"
        data = {
            "name": dataset_name,
            "permission": permission
        }

        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            dataset_id = response.json()["id"]
            logger.info(f"Created new dataset: {dataset_name} with ID: {dataset_id}")
            return dataset_id
        except Exception as e:
            logger.error(f"Failed to create dataset: {str(e)}")
            # Fallback to UUID if dataset creation fails
            fallback_id = str(uuid.uuid4())
            logger.warning(f"Using fallback dataset ID: {fallback_id}")
            return fallback_id 