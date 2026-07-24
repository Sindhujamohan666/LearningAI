"""
Layer 3: Test Plan Creator Tool
Deterministic, atomic script to generate test plan using GROQ LLM.
"""

import requests
import json
import sys
import re
from typing import Dict, Any, List

def generate_test_plan(groq_api_key: str, groq_model: str, issue_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate test plan using GROQ API based on JIRA issue data.
    
    Args:
        groq_api_key: GROQ API key
        groq_model: GROQ model name (e.g., openai/gpt-oss-120b)
        issue_data: JIRA issue data (from jira_connector.py)
    
    Returns:
        Dict with success status and test plan or error message
    """
    
    try:
        # Construct system prompt
        system_prompt = """You are a QA test plan expert. Given a JIRA issue, generate 3-5 comprehensive test cases.
For each test case, include:
- A unique ID (TC_001, TC_002, etc.)
- Clear, concise title (max 50 chars)
- Step-by-step execution steps (numbered, 2-5 steps each)
- Expected result (1-2 sentences)
- Priority level (High/Medium/Low)

Format your response as a valid JSON array only. No additional text.
Example format:
[
  {
    "id": "TC_001",
    "title": "Test case title",
    "steps": ["Step 1", "Step 2", "Step 3"],
    "expectedResult": "Expected behavior",
    "priority": "High"
  }
]"""
        
        # Construct user prompt from issue data
        issue_text = f"""Issue: {issue_data.get('key', 'N/A')}
Title: {issue_data.get('summary', 'N/A')}
Type: {issue_data.get('type', 'Feature')}
Priority: {issue_data.get('priority', 'Medium')}

Description:
{issue_data.get('description', 'No description provided')}

Acceptance Criteria:
{issue_data.get('acceptanceCriteria', 'No criteria specified')}

Generate test cases to validate this issue."""
        
        # GROQ API call
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        # Error handling
        if response.status_code == 401:
            return {
                "success": False,
                "error": "Invalid GROQ API key. Check credentials."
            }
        elif response.status_code == 429:
            return {
                "success": False,
                "error": "GROQ API rate limited. Try again later."
            }
        elif response.status_code >= 500:
            return {
                "success": False,
                "error": "GROQ API server error. Try again later."
            }
        elif response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
        
        # Parse response
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if not content:
            return {
                "success": False,
                "error": "Empty response from GROQ. Try again."
            }
        
        # Extract JSON from response
        try:
            # Try direct JSON parse
            test_cases = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if match:
                test_cases = json.loads(match.group(1))
            else:
                # Last resort: wrap in array
                test_cases = json.loads(content.strip())
        
        # Validate and normalize test cases
        if not isinstance(test_cases, list):
            test_cases = [test_cases]
        
        # Ensure required fields
        for tc in test_cases:
            tc.setdefault("id", f"TC_{test_cases.index(tc) + 1:03d}")
            tc.setdefault("title", "Test case")
            tc.setdefault("steps", ["No steps provided"])
            tc.setdefault("expectedResult", "No expected result")
            tc.setdefault("priority", "Medium")
        
        return {
            "success": True,
            "issueId": issue_data.get("key", "N/A"),
            "testCases": test_cases,
            "generatedAt": __import__("datetime").datetime.utcnow().isoformat() + "Z"
        }
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "GROQ request timeout. Try again."
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection error. Check your internet."
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse test plan response: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


if __name__ == "__main__":
    # Test script
    if len(sys.argv) < 3:
        print("Usage: python test_plan_creator.py <groq_api_key> <groq_model> [issue_json]")
        sys.exit(1)
    
    groq_api_key = sys.argv[1]
    groq_model = sys.argv[2]
    
    # Default issue data if not provided
    issue_data = {
        "key": "VWO-48",
        "summary": "Add search functionality to user dashboard",
        "description": "Users need the ability to search through their saved items.",
        "acceptanceCriteria": "Search box appears on dashboard. Search returns matching items within 2 seconds.",
        "type": "Feature",
        "priority": "High"
    }
    
    if len(sys.argv) > 3:
        issue_data = json.loads(sys.argv[3])
    
    result = generate_test_plan(groq_api_key, groq_model, issue_data)
    print(json.dumps(result, indent=2))
