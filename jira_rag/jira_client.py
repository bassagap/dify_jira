from typing import List, Dict, Optional
from jira import JIRA
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
import urllib3

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
        
        # Create a session with custom headers
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        })
        
        # Disable proxy usage
        session.trust_env = False
        
        # Configure JIRA client with the session
        self.client = JIRA(
            server=self.server_url,
            token_auth=self.api_token,  # Use token-based authentication
            options={
                'session': session,
                'verify': False,  # Disable SSL verification
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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