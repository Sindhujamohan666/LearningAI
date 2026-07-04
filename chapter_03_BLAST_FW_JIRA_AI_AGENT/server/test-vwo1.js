const axios = require('axios');

async function run() {
  try {
    const issueKey = 'VWO-1';
    const fetchRes = await axios.post('http://localhost:3001/api/jira/fetch', { issueKey });
    console.log('Fetched issue:', fetchRes.data.issue.key);

    const genRes = await axios.post('http://localhost:3001/api/groq/generate', { issueData: fetchRes.data.issue, model: 'local-mock' });
    const strategy = genRes.data.testStrategy;
    console.log('Generated for:', strategy.generatedFor);
    console.log('Strategy sections:');
    strategy.strategy.forEach((s, i) => {
      console.log(`${i + 1}. ${s.section}: ${s.content}`);
    });

    const mapped = {
      issueId: strategy.generatedFor,
      generatedAt: new Date().toISOString(),
      testCases: strategy.strategy.map((s, idx) => ({
        id: `TS-${idx + 1}`,
        title: s.section,
        priority: 'Medium',
        steps: [s.content],
        expectedResult: s.content
      }))
    };

    console.log('\nMapped test plan JSON:\n', JSON.stringify(mapped, null, 2));
  } catch (err) {
    console.error('Error:', err.message);
  }
}

run();
