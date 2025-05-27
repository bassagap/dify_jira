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
                assignee=issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
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
            assignee=issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
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
            # First, get the project's issue types to find the correct ID
            project = self.client.project(project_key)
            issue_types = self.client.project_issue_types(project_key)
            
            # Find the "Test" issue type or use the first available one
            issue_type = next((it for it in issue_types if it.name == "Test"), issue_types[0])
            
            issue_dict = {
                "project": {"key": project_key},
                "summary": "Test Issue - Automated Creation",
                "description": "This is a test issue created automatically for testing purposes.",
                "issuetype": {"id": "10009"},
                "reporter": {"name": self.email},
                "assignee": {"name": "Unassigned"}
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

    def link_issues(self, inward_key: str, outward_key: str, link_type: str = "Tests", comment: str = None) -> None:
        """
        Link two issues together
        
        Args:
            inward_key: The inward issue key (e.g., 'PROJ-123')
            outward_key: The outward issue key (e.g., 'PROJ-456')
            link_type: The type of link (default: 'Tests')
            comment: Optional comment to add to the link
        """
        try:
            logger.info(f"Linking issues {inward_key} and {outward_key} with type {link_type}")
            
            # Prepare comment data if provided
            comment_data = None
            if comment:
                comment_data = {
                    "body": comment,
                    "visibility": {
                        "type": "role",
                        "value": "Administrators"
                    }
                }
            
            # Use the built-in create_issue_link method
            self.client.create_issue_link(
                type=link_type,
                inwardIssue=inward_key,
                outwardIssue=outward_key,
                comment=comment_data
            )
            
            logger.info(f"Successfully linked issues {inward_key} and {outward_key}")
                
        except Exception as e:
            logger.error(f"Error linking issues: {str(e)}")
            raise 

    def get_test_case_by_summary(self, project_key: str, summary: str) -> Optional[JiraIssue]:
        """
        Check if a test case with the given summary exists in the project.
        """
        jql = f'project = "{project_key}" AND summary ~ "{summary}" AND issuetype = Test'
        issues = self.get_issues(jql_query=jql, max_results=1)
        return issues[0] if issues else None

    def bulk_create_test_issues(
        self,
        project_key: str,
        test_cases: list,
        parent_key: str,
        link_type: str = "Tests",
        labels: Optional[list] = None,
        reporter: Optional[str] = None,
        component: Optional[str] = None
    ) -> list:
        """
        Bulk create test issues, avoiding duplicates, and link them to the parent.
        """
        logger.info(f"Starting bulk_create_test_issues with project_key: {project_key}, parent_key: {parent_key}")
        logger.info(f"Received {len(test_cases)} test cases to process")
        
        issue_fields = []
        summaries = []
        for tc in test_cases:
            summary = tc["scenario_title"]
            logger.info(f"Processing test case: {summary}")
            
            #existing_issue = self.get_test_case_by_summary(project_key, summary)
            #if existing_issue:
            #    logger.info(f"Duplicate found: {summary}, skipping.")
            #    continue

            description = (
                f"Gherkin:\n{tc['gherkin']}\n\n"
                f"Steps to Reproduce:\n" + "\n".join(f"- {step}" for step in tc.get("steps_to_reproduce", [])) +
                f"\n\nExpected Result:\n{tc.get('expected_result', '')}"
            )

            issue_dict = {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": tc.get("test_case_type", "Test")},
                "priority": {"name": tc.get("priority", "Medium")},
                "assignee": {"name": "Unassigned"}  # Set default assignee
            }
            if labels:
                issue_dict["labels"] = labels
                logger.info(f"Adding labels: {labels}")
            if component:
                issue_dict["components"] = [{"name": component}]
                logger.info(f"Adding component: {component}")
            if reporter:
                issue_dict["reporter"] = {"name": reporter}
                logger.info(f"Setting reporter: {reporter}")
            
            logger.info(f"Prepared issue dict: {issue_dict}")
            issue_fields.append(issue_dict)
            summaries.append(summary)

        logger.info(f"Prepared {len(issue_fields)} issues for creation")
        
        # Bulk create issues
        try:
            created_issues = self.client.create_issues(field_list=issue_fields, prefetch=True) if issue_fields else []
            logger.info(f"Successfully created {len(created_issues)} issues")
            logger.info(f"Created issues response: {created_issues}")
        except Exception as e:
            logger.error(f"Error creating issues: {str(e)}")
            raise

        # Link each created issue to the parent
        results = []
        for issue, summary in zip(created_issues, summaries):
            try:
                # Extract issue key with better error handling and logging
                logger.info(f"Processing created issue: {issue}")
                issue_key = None
                
                if isinstance(issue, dict):
                    if 'issue' in issue and hasattr(issue['issue'], 'key'):
                        issue_key = issue['issue'].key
                        logger.info(f"Extracted key from issue object: {issue_key}")
                    elif 'key' in issue:
                        issue_key = issue['key']
                        logger.info(f"Extracted key from dict: {issue_key}")
                elif hasattr(issue, 'key'):
                    issue_key = issue.key
                    logger.info(f"Extracted key from object: {issue_key}")
                else:
                    logger.error(f"Unexpected issue format: {type(issue)}")
                    continue
                
                if not issue_key:
                    logger.error(f"Could not extract key from issue: {issue}")
                    continue
                
                logger.info(f"Linking issue {issue_key} to parent {parent_key}")
                self.link_issues(
                    inward_key=parent_key,
                    outward_key=issue_key,
                    link_type=link_type,
                    comment=f"Test case generated for scenario: {summary}"
                )
                results.append({
                    "test_case_key": issue_key,
                    "summary": summary,
                    "url": f"{self.server_url.rstrip('/')}/browse/{issue_key}",
                    "message": "Test case created and linked."
                })
                logger.info(f"Successfully linked issue {issue_key}")
            except Exception as e:
                logger.error(f"Error linking issue: {str(e)}")
                if issue_key:
                    results.append({
                        "test_case_key": issue_key,
                        "summary": summary,
                        "url": f"{self.server_url.rstrip('/')}/browse/{issue_key}",
                        "message": f"Test case created, but linking failed: {str(e)}"
                    })
        
        logger.info(f"Completed bulk_create_test_issues. Created {len(results)} test cases")
        return results

    def get_linked_issues(self, issue_key: str, link_type: str = None, issue_type: str = "Test") -> list:
        """
        Retrieve all inward linked issues of a given type (e.g., 'Test'), optionally filtered by link type.
        Returns a list of dicts with keys: key, summary, description, link_type, direction.
        """
        try:
            issue = self.client.issue(issue_key)
            linked = []
            for link in issue.fields.issuelinks:
                # Only check inward links (this issue is the target)
                if hasattr(link, "inwardIssue"):
                    linked_issue = link.inwardIssue
                    if (
                        (link_type is None or link.type.name.lower() == link_type.lower())
                        and getattr(linked_issue.fields.issuetype, "name", "").lower() == issue_type.lower()
                    ):
                        linked_issue_dict = self.get_issue(linked_issue.key)
                        linked.append({
                            "key": linked_issue.key,
                            "summary": getattr(linked_issue.fields, "summary", ""),
                            "description": linked_issue_dict.description or "",
                            "link_type": link.type.name
                        })
            return linked
        except Exception as e:
            logger.error(f"Error retrieving linked issues for {issue_key}: {str(e)}")
            return []