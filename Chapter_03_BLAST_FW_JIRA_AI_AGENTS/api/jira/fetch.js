const axios = require('axios');

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ success: false, error: 'Method not allowed' });

  const { baseUrl, email, token, issueKey } = req.body || {};
  const jiraBase = baseUrl || process.env.JIRA_BASE_URL || process.env.VITE_JIRA_BASE_URL;
  const jiraEmail = email || process.env.JIRA_EMAIL || process.env.VITE_JIRA_EMAIL;
  const jiraToken = token || process.env.JIRA_API_TOKEN || process.env.VITE_JIRA_API_TOKEN;

  if (!issueKey) return res.status(400).json({ success: false, error: 'Missing issueKey' });
  if (!jiraBase || !jiraEmail || !jiraToken) return res.status(400).json({ success: false, error: 'Missing JIRA credentials' });

  try {
    const url = `${jiraBase.replace(/\/$/, '')}/rest/api/3/issue/${encodeURIComponent(issueKey)}`;
    const auth = Buffer.from(`${jiraEmail}:${jiraToken}`).toString('base64');
    const r = await axios.get(url, { headers: { Authorization: `Basic ${auth}`, Accept: 'application/json' }, timeout: 10000 });
    return res.json({ success: true, issue: r.data });
  } catch (err) {
    const message = err.response?.data || err.message || 'Failed to fetch JIRA issue';
    return res.status(502).json({ success: false, error: message });
  }
};
