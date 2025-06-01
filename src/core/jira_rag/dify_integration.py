from typing import List, Dict
import requests
import os
from dotenv import load_dotenv
from .jira_client import JiraIssue
import uuid 
import json
from pathlib import Path
import logging
import traceback
from datetime import datetime
import tiktoken
import re
import random

logger = logging.getLogger(__name__)

class DifyConfigurationError(Exception):
    pass

class DifyIntegration:
    def __init__(self, api_key: str = None, base_url: str = None, dataset_id: str = None, advanced_ingestion: bool = False):
        load_dotenv()
        
        self.dataset_api_key = api_key or os.getenv('DIFY_DATASET_API_KEY')
        self.base_url = base_url or os.getenv('DIFY_BASE_URL', 'http://localhost/v1')
        self.dataset_id = dataset_id or os.getenv('DIFY_DATASET_ID')
        self.advanced_ingestion = advanced_ingestion
        
        if not self.dataset_api_key:
            raise ValueError("Missing Dify API key. Please provide it or set DIFY_DATASET_API_KEY environment variable.")
        self.headers = {
            'Authorization': f'Bearer {self.dataset_api_key}',
            'Content-Type': 'application/json'
        }
        try:
            if not self.dataset_id or self.dataset_id == "your-dataset-id":
                self.dataset_id = self.create_dataset(name=None, advanced_ingestion=self.advanced_ingestion)
                logger.info(f"[DIFY] Created new dataset with id: {self.dataset_id}")
            else:
                logger.info(f"[DIFY] Using existing dataset with id: {self.dataset_id}")
        except Exception as e:
            logger.error(f"[DIFY] Error initializing dataset: {e}\n{traceback.format_exc()}")
            raise
    
    def _get_token_count(self, text: str, model: str = "text-embedding-ada-002") -> int:
        try:
            enc = tiktoken.encoding_for_model(model)
            return len(enc.encode(text))
        except Exception as e:
            logger.error(f"[DIFY] Error counting tokens: {str(e)}")
            return len(text) // 4  # fallback estimate

    def _get_chunk_params(self, text: str, default_max=2000, overlap_ratio=0.25):
        token_count = self._get_token_count(text)
        logger.info(f"[DIFY] Token count: {token_count}")
        if token_count <= default_max:
            logger.info(f"[DIFY] Token count is less than default max: {token_count} <= {default_max}")
            return default_max, 0
        else:
            logger.info(f"[DIFY] Token count is greater than default max: {token_count} > {default_max}")
            overlap = int(default_max * overlap_ratio)
            return default_max, overlap

    def _format_issue_for_text(self, issue: Dict, advanced_ingestion: bool = False) -> Dict:
        """Format a Jira issue into a document suitable for Dify ingestion by text"""
        logger.debug(f"[DIFY] Raw issue data: {json.dumps(issue, indent=2)}")
        
        try:
            # Extract values using the helper method
            key = self._get_nested_value(issue, ['key', 'fields.key'], 'Unknown')
            project = self._get_nested_value(issue, ['project.key', 'fields.project.key'], 'Unknown Project')
            issue_type = self._get_nested_value(issue, ['issuetype.name', 'fields.issuetype.name'], 'Unknown Type')
            status = self._get_nested_value(issue, ['status.name', 'fields.status.name'], 'Unknown Status')
            assignee = self._get_nested_value(issue, ['assignee.name', 'fields.assignee.name'], 'Unassigned')
            created = self._get_nested_value(issue, ['created', 'fields.created'], 'Unknown')
            updated = self._get_nested_value(issue, ['updated', 'fields.updated'], 'Unknown')
            summary = self._get_nested_value(issue, ['summary', 'fields.summary'], 'No summary provided')
            description = self._get_nested_value(issue, ['description', 'fields.description'], 'No description provided')

            # Extract issue number from key (e.g., REST-271 -> 271)
            match = re.search(r"(\\d+)$", key)
            issue_number = match.group(1) if match else None

            text_parts = []
            if advanced_ingestion:
                # Build aliases list
                aliases = [key, f"Issue {key}", f"Jira {key}"]
                if issue_number:
                    aliases.append(issue_number)
                    aliases.append(f"Issue {issue_number}")
                    aliases.append(f"Jira {issue_number}")
                aliases_line = "Aliases: " + ", ".join(aliases) + "\n"
                # Build example queries
                example_queries = [
                    f"What is {key} about?",
                    f"How to test {key}?",
                    f"What does {key} fix?",
                    f"How was {key} resolved?",
                    f"Who reported {key}?",
                    f"Who is assigned to {key}?",
                    f"What is the status of {key}?",
                    f"What project is {key} part of?",
                    f"What is the summary of {key}?",
                    f"Give a test plan for {key}",
                    f"What is the acceptance criteria for {key}?",
                    f"What is the impact of {key}?",
                    f"What is the root cause of {key}?",
                    f"What is the fix for {key}?",
                    f"What is the priority of {key}?",
                    f"What is the type of {key}?",
                    f"When was {key} created?",
                    f"When was {key} updated?",
                    f"What is the description of {key}?",
                    f"What is the context for {key}?",
                    f"How does {key} relate to the product/company/project?"
                ]
                if issue_number:
                    example_queries += [
                        f"What is issue {issue_number} about?",
                        f"How to test issue {issue_number}?",
                        f"Who reported issue {issue_number}?",
                        f"Who is assigned to issue {issue_number}?",
                        f"What is the status of issue {issue_number}?",
                        f"What project is issue {issue_number} part of?",
                        f"What is the summary of issue {issue_number}?",
                        f"Give a test plan for issue {issue_number}",
                        f"What is the acceptance criteria for issue {issue_number}?",
                        f"What is the impact of issue {issue_number}?",
                        f"What is the root cause of issue {issue_number}?",
                        f"What is the fix for issue {issue_number}?",
                        f"What is the priority of issue {issue_number}?",
                        f"What is the type of issue {issue_number}?",
                        f"When was issue {issue_number} created?",
                        f"When was issue {issue_number} updated?",
                        f"What is the description of issue {issue_number}?",
                        f"What is the context of issue {issue_number}?",
                        f"How does issue {issue_number} relate to the product/company/project?"
                    ]
                example_queries_line = "Example queries:\n- " + "\n- ".join(example_queries) + "\n"
                text_parts.append(aliases_line)
                text_parts.append(example_queries_line)
            text_parts.append(f"Summary: {summary}\n\nJira Issue: {key}\nProject: {project}\nType: {issue_type}\nStatus: {status}\nAssignee: {assignee}\nCreated: {created}\nUpdated: {updated}\n\nDescription:\n{description}\n")
            text = "".join(text_parts)
            # Set your desired chunking config
            max_tokens, chunk_overlap = 2000, 400
            process_rule = {
                "mode": "custom",
                "rules": {
                    "pre_processing_rules": [
                        {"id": "remove_extra_spaces", "enabled": True},
                        {"id": "remove_urls_emails", "enabled": False}
                    ],
                    "segmentation": {
                        "separator": "###CHUNK###",
                        "max_tokens": max_tokens,
                        "chunk_overlap": chunk_overlap
                    }
                }
            }
            logger.info(f"[DIFY] Document '{key}': process_rule sent to Dify: {json.dumps(process_rule)}")
            doc = {
                "name": f"Jira Issue {key}",
                "text": text,
                "indexing_technique": "high_quality",
                "process_rule": process_rule
            }
            logger.info(f"[DIFY] Full request body: {json.dumps(doc)}")
            return doc
        except Exception as e:
            logger.error(f"[DIFY] Error formatting issue: {str(e)}\n{traceback.format_exc()}")
            raise
    
    def _format_issue_metadata(self, issue: Dict, document_id: str, metadata_id:str):
        # Handle both JiraIssue objects and dictionary issues
        issue_key = issue.key if isinstance(issue, JiraIssue) else issue['key']
        return {"operation_data": [{"document_id": document_id, "metadata_list":[{"id": metadata_id, "value": issue_key, "name": "issue_key"}]}]}
    
    def _enable_builtin_metadata(self):
        url = f"{self.base_url}/datasets/{self.dataset_id}/metadata/built-in/enable"
        try:
            logger.info(f"[DIFY] Enabling built-in metadata: POST {url}")
            response = requests.post(url, headers=self.headers)
            logger.info(f"[DIFY] Response {response.status_code}: {response.text}")
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"[DIFY] Error enabling built-in metadata: {e}\n{traceback.format_exc()}")
            raise
    
        
    def _create_knowledge_metadata(self):
        url = f"{self.base_url}/datasets/{self.dataset_id}/metadata"
        metadata= {"type": "string", "name": "issue_key"}
        try:
            logger.info(f"[DIFY] Creating knowledge metadata: POST {url} {metadata}")
            response = requests.post(url, headers=self.headers, json=metadata)
            logger.info(f"[DIFY] Response {response.status_code}: {response.text}")
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"[DIFY] Error creating knowledge metadata: {e}\n{traceback.format_exc()}")
            raise
        
    def ingest_issues(self, issues: List[Dict], advanced_ingestion: bool = False) -> List[Dict]:
        """
        Ingest Jira issues into Dify Knowledge Base (Dataset) as documents
        Args:
            issues: List of JiraIssue objects or dictionaries to ingest
            advanced_ingestion: Whether to use advanced ingestion (aliases and queries)
        Returns:
            List of responses from Dify API
        """
        responses = []
        try:
            logger.info(f"[DIFY] Starting ingestion of {len(issues)} issues")
            self._enable_builtin_metadata()
            metadata_id = self._create_knowledge_metadata().json()["id"]
            logger.info(f"[DIFY] Created metadata with ID: {metadata_id}")
            
            for idx, issue in enumerate(issues, 1):
                try:
                    logger.info(f"[DIFY] Processing issue {idx}/{len(issues)}: {issue.key if hasattr(issue, 'key') else issue.get('key', 'unknown')}")
                    url = f"{self.base_url}/datasets/{self.dataset_id}/document/create-by-text"
                    data = self._format_issue_for_text(issue, advanced_ingestion=advanced_ingestion)
                    logger.debug(f"[DIFY] Formatted issue data: {json.dumps(data, indent=2)}")
                    
                    logger.info(f"[DIFY] Creating document: POST {url}")
                    response = requests.post(url, headers=self.headers, json=data)
                    logger.debug(f"[DIFY] Create document response: {response.text}")
                    response.raise_for_status()
                    responses.append(response.json())
                    
                    document_id = response.json()["document"]["id"]
                    logger.info(f"[DIFY] Document created with ID: {document_id}")
                    
                    metadata = self._format_issue_metadata(issue=issue, document_id=document_id, metadata_id=metadata_id)
                    url_metadata = f"{self.base_url}/datasets/{self.dataset_id}/documents/metadata"
                    logger.info(f"[DIFY] Attaching metadata: POST {url_metadata}")
                    response = requests.post(url_metadata, headers=self.headers, json=metadata)
                    logger.debug(f"[DIFY] Metadata response: {response.text}")
                    response.raise_for_status()
                    responses.append(response.json())
                    
                except Exception as e:
                    error_msg = f"[DIFY] Error processing issue {idx}: {str(e)}"
                    logger.error(f"{error_msg}\n{traceback.format_exc()}")
                    continue
                    
            logger.info(f"[DIFY] Completed ingestion. Successfully processed {len(responses)//2} issues")
            return responses
        except Exception as e:
            error_msg = f"[DIFY] Error in ingest_issues: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise

    def ingest_json_file(self, json_file_path: str, advanced_ingestion: bool = False) -> List[Dict]:
        """
        Ingest issues from a JSON file into Dify Knowledge Base
        Args:
            json_file_path: Path to the JSON file containing Jira issues
            advanced_ingestion: Whether to use advanced ingestion (aliases and queries)
        Returns:
            List of responses from Dify API
        """
        try:
            logger.info(f"[DIFY] Reading JSON file: {json_file_path}")
            with open(json_file_path, 'r') as f:
                content = f.read()
                logger.debug(f"[DIFY] Raw JSON content: {content[:500]}...")  # Log first 500 chars
                data = json.loads(content)
            
            # Check if this is a summary file
            if json_file_path.endswith('_SUMMARY.json'):
                logger.info("[DIFY] Detected summary file, processing as a single document")
                # If it's a list, use the first item as the summary dict
                if isinstance(data, list):
                    if len(data) == 0:
                        raise ValueError("Summary file is an empty list!")
                    summary_data = data[0]
                else:
                    summary_data = data
                return self._ingest_summary_file(summary_data, json_file_path)
            
            # Handle different data structures
            if isinstance(data, list):
                logger.info(f"[DIFY] Processing list of {len(data)} items")
                return self.ingest_issues(data, advanced_ingestion=advanced_ingestion)
            elif isinstance(data, dict):
                if 'issues' in data:
                    logger.info(f"[DIFY] Processing issues from 'issues' field")
                    return self.ingest_issues(data['issues'], advanced_ingestion=advanced_ingestion)
                else:
                    logger.info("[DIFY] Processing single issue document")
                    return self.ingest_issues([data], advanced_ingestion=advanced_ingestion)
            else:
                error_msg = f"Unexpected data type in JSON file: {type(data)}"
                logger.error(f"[DIFY] {error_msg}")
                raise ValueError(error_msg)
                
        except json.JSONDecodeError as e:
            error_msg = f"[DIFY] Invalid JSON format in file {json_file_path}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise
        except Exception as e:
            error_msg = f"[DIFY] Error ingesting JSON file {json_file_path}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise

    def _ingest_summary_file(self, data: Dict, file_path: str) -> List[Dict]:
        """
        Process a summary file as multiple documents, one for each major field
        """
        try:
            logger.info("[DIFY] Formatting summary fields as separate documents")
            project_name = Path(file_path).stem.replace('_SUMMARY', '')
            fields = data.get('fields', {})
            responses = []
            url = f"{self.base_url}/datasets/{self.dataset_id}/document/create-by-text"
            
            # Define the fields to ingest and their descriptions
            field_map = [
                ("summary", f"Summary of the project {project_name} is:", fields.get("summary")),
                ("contributors", f"Contributors of the project {project_name} are:", ", ".join(fields.get("contributors", []))),
                ("assignees", f"Assignees of the project {project_name} are:", ", ".join(fields.get("assignees", []))),
                ("reporters", f"Reporters of the project {project_name} are:", ", ".join(fields.get("reporters", []))),
                ("issue_count", f"Issue count of the project {project_name} is:", str(fields.get("issue_count")) if fields.get("issue_count") is not None else None),
                ("type", f"Type of the project {project_name} is:", str(fields.get("type")) if fields.get("type") else None),
            ]
            
            for field, label, value in field_map:
                if value and value.strip():
                    text = f"{label}\n{value}"
                    max_tokens, chunk_overlap = self._get_chunk_params(text)
                    process_rule = {
                        "mode": "custom",
                        "rules": {
                            "pre_processing_rules": [
                                {"id": "remove_extra_spaces", "enabled": True},
                                {"id": "remove_urls_emails", "enabled": False}
                            ],
                            "segmentation": {
                                "separator": "\n\n",
                                "max_tokens": max_tokens,
                                "chunk_overlap": chunk_overlap
                            }
                        }
                    }
                    doc = {
                        "name": f"{label[:60]}",
                        "text": text,
                        "indexing_technique": "high_quality",
                        "process_rule": process_rule
                    }
                    logger.info(f"[DIFY] Creating document for field '{field}': POST {url}")
                    logger.info(f"[DIFY] Full request body: {json.dumps(doc)}")
                    response = requests.post(url, headers=self.headers, json=doc)
                    logger.debug(f"[DIFY] Create document response: {response.text}")
                    response.raise_for_status()
                    responses.append(response.json())
            return responses
        except Exception as e:
            error_msg = f"[DIFY] Error processing summary file: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise

    def _format_summary_text(self, data: Dict, project_name: str) -> str:
        """
        Format summary data into a readable text document
        """
        try:
            summary_parts = [
                f"Project Summary: {project_name}\n",
                f"Generated: {datetime.now().isoformat()}\n\n"
            ]
            
            # Extract fields from the summary structure
            fields = data.get('fields', {})
            
            # Add main summary text
            summary_text = fields.get('summary')
            if summary_text:
                summary_parts.append("Summary:\n")
                summary_parts.append(summary_text + "\n\n")
        
            # Add contributors
            contributors = fields.get('contributors')
            if contributors:
                summary_parts.append("Contributors: " + ", ".join(contributors) + "\n")
            # Add assignees
            assignees = fields.get('assignees')
            if assignees:
                summary_parts.append("Assignees: " + ", ".join(assignees) + "\n")
            # Add reporters
            reporters = fields.get('reporters')
            if reporters:
                summary_parts.append("Reporters: " + ", ".join(reporters) + "\n")
            # Add issue count
            issue_count = fields.get('issue_count')
            if issue_count is not None:
                summary_parts.append(f"Issue count: {issue_count}\n")
            # Add type if present
            type_ = fields.get('type')
            if type_:
                summary_parts.append(f"Type: {type_}\n")
            
            return "".join(summary_parts)
            
        except Exception as e:
            logger.error(f"[DIFY] Error formatting summary text: {str(e)}\n{traceback.format_exc()}")
            return f"Error formatting summary: {str(e)}"

    def _get_nested_value(self, data: Dict, possible_paths: List[str], default: str = "Unknown") -> str:
        """
        Safely get a value from a nested dictionary using multiple possible paths
        """
        for path in possible_paths:
            try:
                value = data
                for key in path.split('.'):
                    value = value.get(key, {})
                if value and value != {}:
                    return str(value)
            except (AttributeError, KeyError, TypeError):
                continue
        return default

    def delete_documents(self, document_ids: List[str]) -> Dict:
        """
        Delete documents from Dify RAG (if supported by your Dify version)
        Args:
            document_ids: List of document IDs to delete
        Returns:
            Response from Dify API
        """
        try:
            response = requests.delete(
                f"{self.base_url}/documents",
                headers=self.headers,
                json={"document_ids": document_ids}
            )
            logger.info(f"[DIFY] Delete documents response {response.status_code}: {response.text}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[DIFY] Error deleting documents: {e}\n{traceback.format_exc()}")
            raise

    def create_dataset(self, name: str = None, permission: str = "only_me", search_method: str = "hybrid_search", advanced_ingestion: bool = False) -> str:
        if name is None:
            mode = "Advanced" if advanced_ingestion else "Basic"
            rand_num = random.randint(100000, 999999)
            name = f"Jira_API_{mode}_{rand_num}"
        url = f"{self.base_url}/datasets"
        data = {
            "name": name,
            "permission": permission,
            "indexing_technique": "high_quality",
            "embedding_model": "text-embedding-ada-002",
            "retrieval_model": {
                "search_method": search_method,
                "reranking_enable": False,
                "top_k": 8,
                "score_threshold_enabled": True,
                "score_threshold": 0.5
            }
        }
        try:
            logger.info(f"[DIFY] Creating dataset: POST {url} {data}")
            response = requests.post(url, headers= self.headers, json=data)
            logger.info(f"[DIFY] Response {response.status_code}: {response.text}")
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                try:
                    error_json = response.json()
                    if "Default model not found for ModelType.TEXT_EMBEDDING" in error_json.get("message", ""):
                        raise DifyConfigurationError(
                            "Dify is not properly configured. Please configure the embeddings method on your Dify server."
                        )
                except Exception:
                    pass  # fallback to generic error
                raise
            dataset_info = response.json()
            logger.info(f"[DIFY] Dataset created: id={dataset_info['id']}, name={dataset_info['name']}")
            return dataset_info["id"] 
        except DifyConfigurationError:
            raise
        except Exception as e:
            logger.error(f"[DIFY] Error creating dataset: {e}\n{traceback.format_exc()}")
            raise 