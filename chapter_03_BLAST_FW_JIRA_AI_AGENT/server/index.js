const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
app.use(bodyParser.json());

// Enable CORS for the frontend origin used during development
app.use(cors({ origin: 'http://localhost:3007' }));

// Simple CORS middleware for local development
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// Simple health
app.get('/api/health', (req, res) => res.json({ ok: true }));

// Validate JIRA: basic check that fields exist
app.post('/api/jira/validate', (req, res) => {
  const { baseUrl, email, token } = req.body || {};
  if (!baseUrl || !email || !token) {
    return res.status(400).json({ success: false, error: 'Missing JIRA credentials' });
  }
  // For development we simply accept provided creds
  return res.json({ success: true, message: 'JIRA credentials accepted (mock)' });
});

// Fetch JIRA issue: return a mocked issue object if issueKey provided
app.post('/api/jira/fetch', (req, res) => {
  const { issueKey } = req.body || {};
  if (!issueKey) return res.status(400).json({ success: false, error: 'Missing issueKey' });

  // Mocked issue payload
  const issue = {
    key: issueKey,
    fields: {
      summary: `Mocked summary for ${issueKey}`,
      description: `This is a mocked description for ${issueKey}. Acceptance criteria: ...`,
      issuetype: { name: 'Story' },
      priority: { name: 'Medium' }
    }
  };

  return res.json({ success: true, issue });
});

// GROQ generate: use a local RICE-POT style template to produce a test strategy
app.post('/api/groq/generate', (req, res) => {
  const { apiKey, model, issueData } = req.body || {};
  if (!issueData) return res.status(400).json({ success: false, error: 'Missing issueData' });

  // Simple local prompt/template generation (RICE-POT inspired)
  const strategy = [];
  strategy.push({ section: 'Risk & Context', content: `Issue ${issueData.key}: ${issueData.fields.summary}\n${issueData.fields.description}` });
  strategy.push({ section: 'Intent', content: 'Validate core user journeys and edge cases related to the described feature.' });
  strategy.push({ section: 'Core Scenarios', content: '1) Happy path; 2) Authentication/Authorization; 3) Error handling; 4) Data validation' });
  strategy.push({ section: 'Exploratory Focus', content: 'State transitions, boundary values, and performance under small load.' });
  strategy.push({ section: 'Prioritization', content: 'Smoke -> Core scenarios -> Edge cases -> Regression' });

  return res.json({ success: true, testStrategy: { generatedFor: issueData.key, modelUsed: model || 'local-mock', strategy } });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`Mock API server listening on port ${PORT}`));
