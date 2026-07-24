"""
Layer 3: JIRA Connector Tool
Deterministic, atomic script to fetch JIRA issue details via REST API.
"""

import requests
import base64
import json
import sys
from typing import Dict, Any

def fetch_jira_issue(base_url: str, email: str, token: str, issue_key: str) -> Dict[str, Any]:
    """
    Fetch JIRA issue details using Basic Auth.
    
    Args:
        base_url: JIRA instance URL (e.g., https://your-jira.atlassian.net)
        email: JIRA user email
        token: JIRA API token
        issue_key: JIRA issue ID (e.g., VWO-48)
    
    Returns:
        Dict with success status and issue data or error message
    """
    
    try:
        # Construct API endpoint
        url = f"{base_url}/rest/api/3/issues/{issue_key}"
        
        # Basic Auth header
        auth_string = f"{email}:{token}"
        auth_bytes = auth_string.encode("utf-8")
        auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json"
        }
        
        # Fetch issue
        response = requests.get(url, headers=headers, timeout=10)
        
        # Error handling
        if response.status_code == 401:
            return {
                "success": False,
                "error": "Authentication failed. Check email and token."
            }
        elif response.status_code == 404:
            return {
                "success": False,
                "error": f"Issue {issue_key} not found."
            }
        elif response.status_code >= 500:
            return {
                "success": False,
                "error": "JIRA API server error. Try again later."
            }
        elif response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
        
        # Parse response
        data = response.json()
        
        # Extract relevant fields
        issue = {
            "key": data.get("key", issue_key),
            "summary": data.get("fields", {}).get("summary", ""),
            "description": data.get("fields", {}).get("description", ""),
            "acceptanceCriteria": "",  # Custom field, may vary
            "type": data.get("fields", {}).get("issuetype", {}).get("name", "Task"),
            "priority": data.get("fields", {}).get("priority", {}).get("name", "Medium")
        }
        
        # Try to extract acceptance criteria from description or custom field
        description = issue.get("description", "")
        if "acceptance criteria" in description.lower():
            issue["acceptanceCriteria"] = description
        
        return {
            "success": True,
            "issue": issue
        }
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout. Check your connection."
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection error. Check JIRA base URL."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


if __name__ == "__main__":
    # Test script
    if len(sys.argv) < 5:
        print("Usage: python jira_connector.py <base_url> <email> <token> <issue_key>")
        sys.exit(1)
    
    base_url = sys.argv[1]
    email = sys.argv[2]
    token = sys.argv[3]
    issue_key = sys.argv[4]
    
    result = fetch_jira_issue(base_url, email, token, issue_key)
    print(json.dumps(result, indent=2))
