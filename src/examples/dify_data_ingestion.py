from jira_rag.jira_client import JiraClient
from jira_rag.dify_integration import DifyIntegration
import os
from dotenv import load_dotenv
import logging
from pathlib import Path
import glob
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def ingest_json_files(dify: DifyIntegration, dataset_dir: str = "jira_rag/dataset", specific_file: str = None):
    """
    Ingest JSON files from the dataset directory.
    Args:
        dify: DifyIntegration instance
        dataset_dir: Directory containing JSON files
        specific_file: Optional specific JSON file to ingest
    """
    if specific_file:
        json_files = [specific_file]
        if not os.path.exists(specific_file):
            logger.error(f"Specified file {specific_file} does not exist")
            return
    else:
        json_files = glob.glob(os.path.join(dataset_dir, "*.json"))
        if not json_files:
            logger.warning(f"No JSON files found in {dataset_dir}")
            return
    
    for json_file in json_files:
        try:
            logger.info(f"Ingesting JSON file: {json_file}")
            response = dify.ingest_json_file(json_file)
            logger.info(f"Successfully ingested {json_file}")
            logger.debug(f"Ingestion response: {response}")
        except Exception as e:
            logger.error(f"Error ingesting {json_file}: {str(e)}")

def ingest_jira_issues(dify: DifyIntegration, jira_client: JiraClient, project: str = "QAREF"):
    """
    Ingest issues from Jira.
    Args:
        dify: DifyIntegration instance
        jira_client: JiraClient instance
        project: Jira project key to fetch issues from
    """
    logger.info(f"Fetching issues from {project} project...")
    jql_query = f"project = {project} ORDER BY created DESC"
    issues = jira_client.get_issues(jql_query, max_results=100)
    
    logger.info(f"Found {len(issues)} issues from {project} project")
    
    if issues:
        logger.info("Ingesting issues into Dify RAG...")
        response = dify.ingest_issues(issues)
        logger.info(f"Ingestion response: {response}")
    else:
        logger.warning(f"No issues found in {project} project")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Ingest Jira issues or JSON files into Dify RAG')
    
    # Create a mutually exclusive group for ingestion options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--jira', action='store_true', help='Ingest issues from Jira into Dify')
    group.add_argument('--all-json', action='store_true', help='Ingest all JSON files from dataset directory')
    group.add_argument('--json', type=str, help='Ingest a specific JSON file from dataset directory')
    group.add_argument('--create-test', action='store_true', help='Create a test issue in Jira')
    group.add_argument('--fetch-jira', action='store_true', help='Fetch issues from Jira without Dify integration')
    
    # Optional arguments
    parser.add_argument('--project', type=str, default='QAREF',
                      help='Jira project key to fetch issues from (default: QAREF)')
    parser.add_argument('--dataset-dir', type=str, default='jira_rag/dataset',
                      help='Directory containing JSON files (default: jira_rag/dataset)')
    parser.add_argument('--max-results', type=int, default=100,
                      help='Maximum number of issues to fetch (default: 100)')
    
    return parser.parse_args()

def create_test_issue(jira_client: JiraClient, project: str = "QAREF"):
    """
    Create a test issue in Jira.
    Args:
        jira_client: JiraClient instance
        project: Jira project key to create the issue in
    """
    logger.info(f"Creating test issue in {project} project...")
    try:
        issue = jira_client.create_test_issue(project)
        logger.info(f"Successfully created test issue: {issue.key}")
        logger.info(f"Summary: {issue.summary}")
        logger.info(f"Status: {issue.status}")
        logger.info(f"Description: {issue.description}")
        
    except Exception as e:
        logger.error(f"Error creating test issue: {str(e)}")
        raise

def fetch_jira_issues(jira_client: JiraClient, project: str = "QAREF", max_results: int = 100):
    """
    Fetch issues from Jira without Dify integration.
    Args:
        jira_client: JiraClient instance
        project: Jira project key to fetch issues from
        max_results: Maximum number of issues to fetch
    """
    logger.info(f"Fetching issues from {project} project...")
    jql_query = f"project = {project} ORDER BY created DESC"
    issues = jira_client.get_issues(jql_query, max_results=max_results)
    
    logger.info(f"Found {len(issues)} issues from {project} project")
    
    for issue in issues:
        logger.info(f"\nIssue: {issue.key}")
        logger.info(f"Summary: {issue.summary}")
        logger.info(f"Status: {issue.status}")
        logger.info(f"Type: {issue.issue_type}")
        logger.info(f"Created: {issue.created}")
        logger.info(f"Updated: {issue.updated}")
        if issue.assignee:
            logger.info(f"Assignee: {issue.assignee}")
        logger.info("-" * 80)

def main():
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Load environment variables
        load_dotenv()
        
        # Check for required environment variables
        check_env_vars()
        
        # Print environment variables (without sensitive data)
        logger.info("Environment variables loaded successfully")
        logger.info(f"JIRA_SERVER_URL: {os.getenv('JIRA_SERVER_URL')}")
        logger.info(f"JIRA_EMAIL: {os.getenv('JIRA_EMAIL')}")
        logger.info("JIRA_API_TOKEN: [REDACTED]")
        logger.info(f"NO_PROXY: {os.getenv('NO_PROXY')}")
        
        if args.jira or args.create_test or args.fetch_jira:
            # Initialize Jira client
            logger.info("Initializing Jira client...")
            jira_client = JiraClient()
            
            # Test connection
            logger.info("Testing Jira connection...")
            server_info = jira_client.client.server_info()
            logger.info(f"Connected to Jira server: {server_info['serverTitle']} (Version: {server_info['version']})")
            
            if args.jira:
                # Initialize Dify integration for ingestion
                logger.info("Initializing Dify integration...")
                dify = DifyIntegration()
                ingest_jira_issues(dify, jira_client, args.project)
            elif args.create_test:
                create_test_issue(jira_client, args.project)
            elif args.fetch_jira:
                fetch_jira_issues(jira_client, args.project, args.max_results)
            
        elif args.all_json or args.json:
            # Initialize Dify integration for JSON ingestion
            logger.info("Initializing Dify integration...")
            dify = DifyIntegration()
            
            if args.all_json:
                # Ingest all JSON files
                ingest_json_files(dify, args.dataset_dir)
            elif args.json:
                # Ingest specific JSON file
                json_path = os.path.join(args.dataset_dir, args.json) if not os.path.isabs(args.json) else args.json
                ingest_json_files(dify, args.dataset_dir, json_path)
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 