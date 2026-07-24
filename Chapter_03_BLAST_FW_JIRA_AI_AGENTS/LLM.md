# Gemini - Project Constitution

## Project Overview
- **Name**: JIRA Test Plan Generator (React)
- **North Star**: User provides JIRA credentials + issue ID → app fetches issue details → GROQ generates test plan → display in UI
- **Tech Stack**: React, TypeScript, Axios, GROQ SDK

---

## Data Schema

### Input: Settings (stored in localStorage)
```json
{
  "jira": {
    "baseUrl": "https://your-jira.atlassian.net",
    "email": "user@example.com",
    "token": "jira_api_token_here"
  },
  "groq": {
    "apiKey": "gsk_xxxxx",
    "model": "openai/gpt-oss-120b"
  }
}
```

### Input: JIRA Issue ID (user input)
```json
{
  "issueId": "VWO-48"
}
```

### Output: Fetched JIRA Issue
```json
{
  "key": "VWO-48",
  "summary": "Issue summary",
  "description": "Issue description text",
  "acceptanceCriteria": "Acceptance criteria if available",
  "type": "Bug|Feature|Task"
}
```

### Output: Generated Test Plan
```json
{
  "issueId": "VWO-48",
  "testCases": [
    {
      "id": "TC_001",
      "title": "Test case title",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "expectedResult": "Expected behavior",
      "priority": "High|Medium|Low"
    }
  ],
  "generatedAt": "2026-06-07T10:30:00Z"
}
```

---

## Behavioral Rules
1. **Settings Storage**: localStorage (session-based, cleared on browser close)
2. **Token Security**: No encryption in v1, warn user about localStorage security
3. **Validation**: Before generation, validate JIRA connectivity and GROQ API key
4. **Error Handling**: Show user-friendly error messages, no sensitive data exposure
5. **Rate Limiting**: No explicit rate limiting in v1, rely on API rate limits
6. **Retry Logic**: Single attempt per generation, fail gracefully
7. **UI States**: Loading → Generate → Display → Copy/Export option

---

## Architectural Invariants
- Fetch JIRA → Validate response → Generate via GROQ → Format output → Display in UI
- No backend required (direct API calls from React)
- All settings ephemeral; user re-enters credentials per session
- GROQ model is deterministic; same issue should produce similar test plans

---

## Implementation Status

### Phase 2: Link (Connectivity) - COMPLETE
- `.env` template created with JIRA and GROQ variables
- JIRA Connector (tools/jira_connector.py) implemented with Basic Auth
- Test Plan Creator (tools/test_plan_creator.py) implemented with GROQ API
- Both tools handle errors, timeouts, and edge cases

### Phase 3: Architect (3-Layer Build) - COMPLETE
- Layer 1: 3 SOPs created (01_jira_connector_sop.md, 02_test_plan_generator_sop.md, 03_data_flow_architecture.md)
- Layer 2: Navigation logic in React App.jsx (state management, routing, error handling)
- Layer 3: Python tools are atomic, stateless, and deterministic
- Layer 4: React UI with components (SettingsPanel, IssueInput, TestPlanDisplay)

### Phase 4: Stylize (UI/UX) - COMPLETE
- Settings panel with JIRA and GROQ configuration form
- Issue input with ID field and generate button
- Test plan display with prioritization, steps, and expected results
- Export options: copy to clipboard, download JSON, download Markdown
- Professional CSS styling with gradient backgrounds and responsive design
- Loading states, error messages, status indicators

### Phase 5: Trigger (Deployment) - READY
- Cloud deployment documentation pending
- Production environment setup pending
