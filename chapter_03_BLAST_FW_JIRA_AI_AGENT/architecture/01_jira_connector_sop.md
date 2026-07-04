# SOP: JIRA Connector

## Purpose
Fetch JIRA issue details using JIRA REST API authentication.

## Inputs
- `base_url`: JIRA instance URL (e.g., `https://your-jira.atlassian.net`)
- `email`: JIRA user email
- `token`: JIRA API token (Basic Auth)
- `issue_key`: JIRA issue ID (e.g., `VWO-48`)

## Process
1. **Authenticate**: Use Basic Auth (email:token)
2. **Fetch Issue**: GET `/rest/api/3/issues/{issue_key}`
3. **Extract Fields**:
   - `key`: Issue ID
   - `summary`: Title
   - `description`: Full description
   - `labels`: Tags/categories
   - `issuetype.name`: Bug, Feature, etc.
   - `customfield_xxxxx`: Acceptance criteria (if available)
4. **Validate Response**: Ensure all required fields are present
5. **Return**: Structured JSON object

## Outputs
```json
{
  "success": true,
  "issue": {
    "key": "VWO-48",
    "summary": "Add search functionality",
    "description": "Users need ability to search...",
    "acceptanceCriteria": "Acceptance criteria text",
    "type": "Feature",
    "priority": "High"
  }
}
```

## Error Handling
- **401**: Invalid credentials → Return "Authentication failed"
- **404**: Issue not found → Return "Issue does not exist"
- **5xx**: Server error → Return "JIRA API unavailable, retry later"

## Edge Cases
- Missing optional fields (e.g., acceptance criteria) → Set to empty string
- Rate limiting → Single attempt, no retry in v1
