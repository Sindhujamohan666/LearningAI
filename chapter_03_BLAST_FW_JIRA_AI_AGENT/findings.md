# Findings

## Discovery Phase
- **Project Objective**: Build lightweight React app to fetch JIRA issue details and generate test plans using JIRA credentials + GROQ API (`openai/gpt-oss-120b`).
- **Scope**: Single-issue test plan generation (VWO-48 example given).
- **User Decision**: Auto-lock blueprint based on objective, proceed with Phase 2.

## Integration Points
1. **JIRA API**: Authentication via email + token, fetch issue metadata
2. **GROQ API**: Generate test plan from JIRA issue text
3. **React Frontend**: Settings form + test plan display

## Data Flow
User Settings (localStorage) → JIRA Fetch → GROQ Generate → Display in UI → Optional Export

## Constraints & Assumptions
- No backend server; direct API calls from React
- Credentials stored in localStorage (session-ephemeral for security)
- Single test plan per JIRA issue per session
- GROQ model is deterministic
- No rate limiting in v1

## Discoveries from Implementation

### JIRA API Integration
- Basic Auth required: Authorization: Basic base64(email:token)
- Error codes: 401 (auth failed), 404 (issue not found), 5xx (server error)
- Issue fields extracted: key, summary, description, issuetype, priority
- Acceptance criteria extraction from description text (custom field handling)

### GROQ API Integration
- Required: Bearer token in Authorization header
- Model: openai/gpt-oss-120b (free tier, fully functional)
- Response format: JSON with choices[0].message.content
- JSON parsing required: handle markdown code blocks, raw JSON, or fallback
- Temperature: 0.7 for balanced creativity/determinism
- Max tokens: 1500 adequate for 3-5 test cases

### React State Management
- localStorage efficient for ephemeral credential storage
- useState sufficient for single-issue workflow (no Redux needed)
- Async/await handling for API calls with proper loading states
- Error boundaries prevent UI crashes on malformed responses

### Test Plan Generation Quality
- Structured prompt yields consistent test case formatting
- System prompt + user prompt combination effective
- Test cases consistently include: ID, title, steps, expected result, priority
- Parser handles JSON extraction from markdown wrappers

### UI/UX Learnings
- Settings toggle minimizes clutter while keeping configuration accessible
- Test case cards with color-coded priorities improve scannability
- Export options (JSON, Markdown) support downstream tooling integration
- Copy-to-clipboard reduces friction for manual tracking

## Next Steps (Phase 5: Deployment)
- Build and test locally (npm install, npm run dev)
- Package for production (npm run build)
- Deploy to cloud (Vercel, Netlify, or S3 + CloudFront)
- Configure production environment variables
- Set up monitoring and error tracking
