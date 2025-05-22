from typing import List, Dict, Optional
from jira import JIRA
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
import urllib3
import logging
import base64

# Configure logging
logger = logging.getLogger(__name__)

# Add Jira domain to NO_PROXY
os.environ['NO_PROXY'] = os.environ.get('NO_PROXY', '') + ',jira.biscrum.com'

class JiraIssue(BaseModel):
    key: str
    summary: str
    description: Optional[str]
    status: str
    assignee: Optional[str]
    created: str
    updated: str
    project: str
    issue_type: str

class JiraClient:
    def __init__(self, server_url: Optional[str] = None, 
                 email: Optional[str] = None, 
                 api_token: Optional[str] = None):
        load_dotenv()
        
        self.server_url = server_url or os.getenv('JIRA_SERVER_URL')
        self.email = email or os.getenv('JIRA_EMAIL')
        self.api_token = api_token or os.getenv('JIRA_API_TOKEN')
        
        if not all([self.server_url, self.email, self.api_token]):
            raise ValueError("Missing required Jira credentials. Please provide them or set environment variables.")

        
        # Disable proxy usage
        #self.session.trust_env = False
        
        # Configure JIRA client with the session
        self.client = JIRA(
            server=self.server_url,
            token_auth=self.api_token,  # Use token-based authentication
            options={
                'verify': False,  # Disable SSL verification
                'headers': {
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            }
        )
    
    def get_issues(self, jql_query: str, max_results: int = 100) -> List[JiraIssue]:
        """
        Fetch issues from Jira using a JQL query
        
        Args:
            jql_query: JQL query string
            max_results: Maximum number of results to return
            
        Returns:
            List of JiraIssue objects
        """
        issues = self.client.search_issues(jql_query, maxResults=max_results)
        
        return [
            JiraIssue(
                key=issue.key,
                summary=issue.fields.summary,
                description=issue.fields.description,
                status=issue.fields.status.name,
                assignee=issue.fields.assignee.displayName if issue.fields.assignee else None,
                created=issue.fields.created,
                updated=issue.fields.updated,
                project=issue.fields.project.name,
                issue_type=issue.fields.issuetype.name
            )
            for issue in issues
        ]
    
    def get_issue(self, issue_key: str) -> JiraIssue:
        """
        Fetch a single issue by its key
        
        Args:
            issue_key: The Jira issue key (e.g., 'PROJ-123')
            
        Returns:
            JiraIssue object
        """
        issue = self.client.issue(issue_key)
        
        return JiraIssue(
            key=issue.key,
            summary=issue.fields.summary,
            description=issue.fields.description,
            status=issue.fields.status.name,
            assignee=issue.fields.assignee.displayName if issue.fields.assignee else None,
            created=issue.fields.created,
            updated=issue.fields.updated,
            project=issue.fields.project.name,
            issue_type=issue.fields.issuetype.name
        )

    def create_test_issue(self, project_key: str) -> JiraIssue:
        """
        Create a test issue with hardcoded values
        
        Args:
            project_key: The Jira project key (e.g., 'PROJ')
            
        Returns:
            JiraIssue object of the created issue
        """
        try:
            
            issue_dict = {
                "project": {"key": project_key},
                "summary": "Test Issue - Automated Creation",
                "description": "This is a test issue created automatically for testing purposes.",
                "issuetype": {"id": "10009"},
                "reporter": {"name": self.email}
                
            }
            logger.info(f"issue_dict: {issue_dict}")
            logger.info(f"Creating test issue in {project_key} project...")
            logger.info(f"Issue dict: {issue_dict}")
            new_issue = self.client.create_issue(fields=issue_dict)
            logger.info(f"New issue created: {new_issue.key}")
        except Exception as e:
            logger.error(f"Error creating test issue: {str(e)}")
            raise
        
        return self.get_issue(new_issue.key) 