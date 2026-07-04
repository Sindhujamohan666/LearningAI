# SOP: Test Plan Generator

## Purpose
Generate deterministic test plan from JIRA issue details using GROQ LLM.

## Inputs
- `issue_data`: Fetched JIRA issue (from JIRA Connector)
  - `key`: Issue ID
  - `summary`: Title
  - `description`: Full description
  - `acceptanceCriteria`: Acceptance criteria
  - `type`: Issue type (Bug, Feature, Task)
- `groq_api_key`: GROQ API key
- `groq_model`: Model name (`openai/gpt-oss-120b`)

## Process
1. **Construct Prompt**: Build a system + user prompt that instructs GROQ to generate test cases
2. **Call GROQ API**: POST to GROQ endpoint with prompt
3. **Parse Response**: Extract test cases from LLM output
4. **Structure Output**: Format as JSON array of test cases
5. **Validate**: Ensure each test case has required fields

## System Prompt
```
You are a QA test plan expert. Given a JIRA issue, generate 3-5 comprehensive test cases.
For each test case, include:
- A unique ID (TC_001, TC_002, etc.)
- Clear title
- Step-by-step execution steps (numbered)
- Expected result
- Priority level (High/Medium/Low)

Format output as valid JSON array.
```

## Outputs
```json
{
  "success": true,
  "issueId": "VWO-48",
  "testCases": [
    {
      "id": "TC_001",
      "title": "Test case title",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "expectedResult": "Expected behavior description",
      "priority": "High"
    }
  ],
  "generatedAt": "2026-06-07T10:30:00Z"
}
```

## Error Handling
- **401**: Invalid GROQ API key → Return "Authentication failed"
- **Rate Limited**: Backoff → Single attempt, fail gracefully
- **Malformed Response**: Parse failure → Return generic test plan template
- **Empty Issue**: Insufficient data → Return "Insufficient data to generate test plan"

## Edge Cases
- Very long descriptions → Truncate to 2000 chars for prompt
- Missing issue type → Default to "Feature"
- LLM returns non-JSON → Parse as best-effort, provide structure
