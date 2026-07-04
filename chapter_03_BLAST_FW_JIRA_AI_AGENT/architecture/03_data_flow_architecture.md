# SOP: Data Flow Architecture

## End-to-End Flow

```
User Input (JIRA Credentials + Issue ID)
    ↓
[Layer 2: Navigation - Route to JIRA Connector]
    ↓
[Layer 3: Tool - jira_connector.py] → JIRA API
    ↓
Fetch Issue Details (JSON)
    ↓
[Layer 2: Navigation - Validate, Route to Test Plan Generator]
    ↓
[Layer 3: Tool - test_plan_creator.py] → GROQ API
    ↓
Generated Test Plan (JSON)
    ↓
[Layer 4: React Component] → Format & Display in UI
    ↓
User Output (Test Plan + Export/Copy Options)
```

## Layer Responsibilities

### Layer 1: Architecture (SOPs)
- `01_jira_connector_sop.md`: Defines JIRA API contract, error handling
- `02_test_plan_generator_sop.md`: Defines LLM generation contract
- `03_data_flow_architecture.md` (this file): Orchestration logic

### Layer 2: Navigation (Decision Making)
- React component logic determines when to call JIRA vs GROQ
- Handles validation, state management, error routing
- Decides UI transitions (Loading → Success → Display)

### Layer 3: Tools (Deterministic Scripts)
- `tools/jira_connector.py`: JIRA API calls (single responsibility)
- `tools/test_plan_creator.py`: GROQ API calls (single responsibility)
- Stateless, atomic, testable

### Layer 4: UI (React Components)
- Receives formatted JSON outputs
- Renders settings form, loading state, test plan display
- Handles copy-to-clipboard, export to markdown/JSON

## State Management
- Settings: React useState (localStorage on save)
- Issue Data: React useState (temporary, cleared per generation)
- Test Plan: React useState (temporary, clearable)
- Loading: React useState (boolean flag)
- Error: React useState (error message, clearable)

## Error Boundaries
1. JIRA connection fails → Show error, allow retry with different credentials
2. GROQ API fails → Show error, allow user to adjust prompt and retry
3. Parsing fails → Show raw output for manual review
4. Network timeout → Show timeout error with retry option
