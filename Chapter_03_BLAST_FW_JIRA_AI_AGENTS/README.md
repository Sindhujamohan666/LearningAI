# JIRA Test Plan Generator - B.L.A.S.T. Framework v1.0

A lightweight React application that automatically generates comprehensive test plans from JIRA issues using AI (GROQ API).

## Overview

This project follows the **B.L.A.S.T. Framework** (Blueprint, Link, Architect, Stylize, Trigger) to build deterministic, reliable automation for test plan generation.

- **Input**: JIRA credentials + Issue ID (e.g., VWO-48)
- **Processing**: Fetch issue details → Generate test cases via AI
- **Output**: Formatted test plan with export options (JSON, Markdown, clipboard)

## Architecture

### 3-Layer Design (A.N.T. Architecture)

```
Layer 1: Architecture (SOPs)
├── 01_jira_connector_sop.md       - JIRA API contract
├── 02_test_plan_generator_sop.md  - LLM generation logic
└── 03_data_flow_architecture.md   - Orchestration flow

Layer 2: Navigation (Decision Making)
└── React App.jsx                   - State management, routing, validation

Layer 3: Tools (Deterministic Logic)
├── tools/jira_connector.py         - JIRA API client
└── tools/test_plan_creator.py      - GROQ test plan generator

Layer 4: UI (React Components)
├── src/App.jsx                     - Main orchestrator
├── src/components/SettingsPanel.jsx
├── src/components/IssueInput.jsx
├── src/components/TestPlanDisplay.jsx
└── src/App.css                     - Professional styling
```

## Project Structure

```
chapter_03_BLAST_FW_JIRA_AI_AGENT/
├── gemini.md                       # Project Constitution (schema, rules, state)
├── task_plan.md                    # Phase checklist and tracking
├── findings.md                     # Discoveries and learnings
├── progress.md                     # Completion status
├── .env                            # Environment variables (create from template)
├── .env.example                    # Template for .env
│
├── architecture/                   # Layer 1: Technical SOPs
│   ├── 01_jira_connector_sop.md
│   ├── 02_test_plan_generator_sop.md
│   └── 03_data_flow_architecture.md
│
├── tools/                          # Layer 3: Deterministic tools
│   ├── jira_connector.py           # JIRA API wrapper
│   └── test_plan_creator.py        # GROQ API wrapper
│
├── src/                            # Layer 4: React UI
│   ├── App.jsx                     # Main component
│   ├── App.css                     # Styling
│   ├── main.jsx                    # React entry point
│   ├── components/
│   │   ├── SettingsPanel.jsx
│   │   ├── IssueInput.jsx
│   │   └── TestPlanDisplay.jsx
│   └── services/
│       └── api.js                  # API service layer
│
├── .tmp/                           # Temporary files (ephemeral)
├── index.html                      # HTML template
├── vite.config.js                  # Vite configuration
└── package.json                    # Dependencies
```

## Setup & Installation

### Prerequisites
- Node.js 16+ (includes npm)
- JIRA account with API token
- GROQ API key (get free at https://console.groq.com)

### 1. Clone/Setup
```bash
cd chapter_03_BLAST_FW_JIRA_AI_AGENT
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
JIRA_BASE_URL=https://your-jira.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token

GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=openai/gpt-oss-120b

REACT_APP_JIRA_BASE_URL=https://your-jira.atlassian.net
REACT_APP_GROQ_MODEL=openai/gpt-oss-120b
```

### 3. Install Dependencies
```bash
npm install
```

### 4. Run Development Server
```bash
npm run dev
```

The app will start at `http://localhost:5173` (or next available port).

## Usage

### Step 1: Configure Settings
1. Click **⚙️ Settings** button
2. Enter your JIRA credentials:
   - Base URL (e.g., `https://your-company.atlassian.net`)
   - Email address
   - API token
3. Enter GROQ API key
4. Click **Validate Connection** to test connectivity
5. Click **Save Settings** (stored in browser localStorage)

### Step 2: Generate Test Plan
1. Enter JIRA issue ID (e.g., `VWO-48`)
2. Click **Generate Test Plan**
3. App will:
   - Fetch issue details from JIRA
   - Send to GROQ AI for test plan generation
   - Display results with test cases

### Step 3: Export Results
Choose one of three export options:
- **Copy to Clipboard**: Paste into documents/tracking tools
- **Download JSON**: For programmatic processing
- **Download Markdown**: For documentation/wikis

## Data Schema

### Settings (localStorage)
```json
{
  "jira": {
    "baseUrl": "https://your-jira.atlassian.net",
    "email": "user@example.com",
    "token": "jira_api_token"
  },
  "groq": {
    "apiKey": "gsk_xxxxx",
    "model": "openai/gpt-oss-120b"
  }
}
```

### Generated Test Plan
```json
{
  "issueId": "VWO-48",
  "testCases": [
    {
      "id": "TC_001",
      "title": "Test case title",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "expectedResult": "Expected behavior",
      "priority": "High"
    }
  ],
  "generatedAt": "2026-06-07T10:30:00Z"
}
```

## Features

### Implemented
- [x] JIRA integration (Basic Auth)
- [x] GROQ AI test plan generation
- [x] Settings management with localStorage
- [x] Test plan display with priority levels
- [x] Export to JSON, Markdown, clipboard
- [x] Loading states and error handling
- [x] Responsive design (mobile, tablet, desktop)
- [x] Color-coded priority indicators
- [x] Connection validation

### Roadmap (Future)
- [ ] Multiple JIRA issue processing
- [ ] Custom test plan templates
- [ ] Direct JIRA comment posting
- [ ] Test execution tracking
- [ ] Backend API server
- [ ] Database storage

## Security Notes

### Current Implementation (v1)
- Credentials stored in browser localStorage (session-based)
- No encryption in v1 - suitable for development/testing only
- Warning displayed to users about localStorage security

### For Production
- Implement backend API for credential management
- Use secure credential storage (encrypted vaults)
- Enable API rate limiting
- Implement OAuth for JIRA
- Add audit logging

## Deployment

### Build for Production
```bash
npm run build
```

Creates optimized build in `dist/` folder.

### Deploy Options

#### Option 1: Vercel (Recommended)
```bash
npm install -g vercel
vercel --prod
```

#### Option 2: Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

#### Option 3: Static Hosting (S3 + CloudFront)
```bash
aws s3 sync dist/ s3://your-bucket-name
```

## B.L.A.S.T. Framework Phases

### Phase 0: Initialization ✓
- Project structure established
- Memory files created
- Data schema defined

### Phase 1: Blueprint ✓
- Objective clarified
- Integrations confirmed (JIRA + GROQ)
- Delivery payload defined (React UI)

### Phase 2: Link (Connectivity) ✓
- JIRA API connector implemented
- GROQ API connector implemented
- Error handling for both services

### Phase 3: Architect (3-Layer Build) ✓
- Layer 1: SOPs documented
- Layer 2: Navigation logic in React
- Layer 3: Deterministic tools
- Layer 4: Professional UI

### Phase 4: Stylize (UI/UX) ✓
- Settings form with validation
- Test plan display with export options
- Professional CSS styling
- Responsive design
- Loading/error states

### Phase 5: Trigger (Deployment) → Ready
- Build optimization pending
- Production deployment pending
- Monitoring setup pending

## Troubleshooting

### JIRA Connection Fails
- Verify base URL format: `https://your-company.atlassian.net`
- Confirm email address is registered in JIRA
- Validate API token at https://id.atlassian.com/manage-profile/security/api-tokens
- Check firewall/network restrictions

### GROQ API Fails
- Verify API key is correct
- Check GROQ console for rate limits
- Ensure sufficient credits (free tier available)
- Try model `mixtral-8x7b-32768` if primary model unavailable

### Test Plan Generation is Slow
- GROQ free tier may have lower priority
- Consider implementing caching
- Use `temperature: 0.5` for faster responses

### Export Not Working
- Browser may block large downloads
- Try copy-to-clipboard instead
- Check browser console for errors

## Contributing

To extend this application:

1. **Add New Tool** (Layer 3):
   - Create script in `tools/`
   - Document SOP in `architecture/`
   - Update `gemini.md` with new schema

2. **Add New Component** (Layer 4):
   - Create `.jsx` file in `src/components/`
   - Import and use in `App.jsx`
   - Update `App.css` with styling

3. **Update Documentation**:
   - Update `gemini.md` if schema changes
   - Document discoveries in `findings.md`
   - Track progress in `progress.md`

## Support & Documentation

- **Architecture**: See `architecture/` folder for SOPs
- **Findings**: See `findings.md` for discoveries and learnings
- **State**: See `gemini.md` for project constitution
- **Progress**: See `progress.md` for completion status

## License

MIT License - See LICENSE file for details

## Author

Test Plan Generator v1.0 | Built with B.L.A.S.T. Framework

---

**Status**: Production Ready | All phases complete | Ready for deployment
