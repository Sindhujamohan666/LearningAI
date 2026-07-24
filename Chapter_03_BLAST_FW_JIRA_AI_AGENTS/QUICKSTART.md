# Quick Start Guide - 5 Minutes to Running

## 1. Install Dependencies (1 min)
```bash
npm install
```

## 2. Configure Environment (2 min)
Edit `.env` file:
```
JIRA_BASE_URL=https://your-jira.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token
GROQ_API_KEY=your-groq-api-key
```

Get credentials:
- **JIRA Token**: https://id.atlassian.com/manage-profile/security/api-tokens
- **GROQ Key**: https://console.groq.com (free)

## 3. Start Development (1 min)
```bash
npm run dev
```

## 4. Use the App (1 min)
1. Open http://localhost:5173
2. Click Settings ⚙️, enter your JIRA/GROQ credentials
3. Enter JIRA issue ID (e.g., VWO-48)
4. Click Generate Test Plan
5. Export results (JSON, Markdown, or clipboard)

## Deployment Checklist

### Pre-Deployment
- [ ] Test with real JIRA instance
- [ ] Verify GROQ API is responding
- [ ] Test all export formats
- [ ] Test on mobile browser
- [ ] Verify error messages are clear

### Build & Deploy
```bash
# Build for production
npm run build

# Deploy to Vercel
npm install -g vercel
vercel --prod

# OR Deploy to Netlify
netlify deploy --prod --dir=dist
```

### Post-Deployment
- [ ] Test app in production URL
- [ ] Verify credentials work in browser
- [ ] Test export functionality
- [ ] Monitor error logs

## Environment Variables for Production

```
REACT_APP_JIRA_BASE_URL=https://your-jira.atlassian.net
REACT_APP_GROQ_MODEL=openai/gpt-oss-120b
REACT_APP_API_BASE_URL=https://your-api-domain.com/api (optional)
```

## API Integration Notes

### Direct Client-Side (Current Implementation)
- No backend server required
- API calls made directly from React
- Credentials stored in browser localStorage
- Suitable for development/testing

### With Backend (Recommended for Production)
- Backend proxy for API calls
- Credential encryption and secure storage
- Rate limiting and logging
- CORS and security headers

See `architecture/03_data_flow_architecture.md` for detailed flow.
