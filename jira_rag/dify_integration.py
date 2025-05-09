from typing import List, Dict
import requests
import os
from dotenv import load_dotenv
from .jira_client import JiraIssue
import uuid 

class DifyIntegration:
    def __init__(self, api_key: str = None, base_url: str = None, dataset_id: str = None):
        load_dotenv()
        
        self.dataset_api_key = api_key or os.getenv('DIFY_DATASET_API_KEY')
        self.base_url = base_url or os.getenv('DIFY_BASE_URL', 'http://localhost/v1')
        self.dataset_id = dataset_id or os.getenv('DIFY_DATASET_ID')
        
        if not self.dataset_api_key:
            raise ValueError("Missing Dify API key. Please provide it or set DIFY_DATASET_API_KEY environment variable.")
        self.headers = {
            'Authorization': f'Bearer {self.dataset_api_key}',
            'Content-Type': 'application/json'
        }
        if not self.dataset_id:
             self.dataset_id = self.create_dataset(str(uuid.uuid4()))
        
    
    def _format_issue_for_text(self, issue: JiraIssue) -> Dict:
        """Format a Jira issue into a document suitable for Dify ingestion by text"""
        return {
            "name": f"Jira Issue {issue.key}",
            "text": f"""
Jira Issue: {issue.key}
Project: {issue.project}
Type: {issue.issue_type}
Status: {issue.status}
Assignee: {issue.assignee or 'Unassigned'}
Created: {issue.created}
Updated: {issue.updated}
\nSummary: {issue.summary}\n\nDescription:\n{issue.description or 'No description provided'}
""",
            "indexing_technique": "economy",
            "process_rule": {"mode": "automatic"}
        }
    
    def _format_issue_metadata(self, issue: JiraIssue, document_id: str, metadata_id:str):
        return {"operation_data": [{"document_id": document_id, "metadata_list":[{"id": metadata_id, "value": issue.key, "name": "issue_key"}]}]}
    
    def _enable_builtin_metadata(self):
        url = f"{self.base_url}/datasets/{self.dataset_id}/metadata/built-in/enable"
        return requests.post(url, headers=self.headers)
    
        
    def _create_knowledge_metadata(self):
        url = f"{self.base_url}/datasets/{self.dataset_id}/metadata"
        metadata= {"type": "string", "name": "issue_key"}
        return requests.post(url, headers=self.headers, json = metadata)
        
    def ingest_issues(self, issues: List[JiraIssue]) -> List[Dict]:
        """
        Ingest Jira issues into Dify Knowledge Base (Dataset) as documents
        Args:
            issues: List of JiraIssue objects to ingest
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

    def create_dataset(self, name: str, permission: str = "only_me") -> str:
        url = f"{self.base_url}/datasets"
        data = {"name": name, "permission": permission}

        response = requests.post(url, headers= self.headers, json=data)
        response.raise_for_status()
        return response.json()["id"] 