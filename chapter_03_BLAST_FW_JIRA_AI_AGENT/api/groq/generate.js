// Lightweight server-side generator that builds a RICE-POT style strategy
module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ success: false, error: 'Method not allowed' });

  const { issueData, apiKey, model } = req.body || {};

  if (!issueData) return res.status(400).json({ success: false, error: 'Missing issueData' });

  try {
    const strategy = [];
    strategy.push({ section: 'Risk & Context', content: `Issue ${issueData.key}: ${issueData.fields?.summary || ''}\n${issueData.fields?.description || ''}` });
    strategy.push({ section: 'Intent', content: 'Validate core user journeys and edge cases related to the described feature.' });
    strategy.push({ section: 'Core Scenarios', content: '1) Happy path; 2) Authentication/Authorization; 3) Error handling; 4) Data validation' });
    strategy.push({ section: 'Exploratory Focus', content: 'State transitions, boundary values, and performance under small load.' });
    strategy.push({ section: 'Prioritization', content: 'Smoke -> Core scenarios -> Edge cases -> Regression' });

    return res.json({ success: true, testStrategy: { generatedFor: issueData.key, modelUsed: model || process.env.GROQ_MODEL || 'local', strategy } });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message || 'Generation failed' });
  }
};
