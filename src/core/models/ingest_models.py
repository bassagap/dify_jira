from pydantic import BaseModel
from typing import Optional, List

class IngestJiraRequest(BaseModel):
    """Model for Jira ingestion requests."""
    project: Optional[str] = None
    jql: Optional[str] = None
    max_results: Optional[int] = 100

class IngestJsonRequest(BaseModel):
    """Model for JSON file ingestion requests."""
    file_names: List[str]  # List of file names
    dataset_dir: Optional[str] = "jira_rag/dataset" 