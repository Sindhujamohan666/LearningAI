import React from 'react';

/**
 * TestPlanDisplay Component
 * Renders generated test plan with export/copy options
 */
const TestPlanDisplay = ({ testPlan, isLoading, error }) => {
  const copyToClipboard = () => {
    const text = formatTestPlanAsText(testPlan);
    navigator.clipboard.writeText(text).then(() => {
      alert('Test plan copied to clipboard!');
    });
  };

  const downloadAsJson = () => {
    const element = document.createElement('a');
    element.href = URL.createObjectURL(new Blob([JSON.stringify(testPlan, null, 2)], { type: 'application/json' }));
    element.download = `test-plan-${testPlan.issueId}-${new Date().getTime()}.json`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const downloadAsMarkdown = () => {
    const text = formatTestPlanAsMarkdown(testPlan);
    const element = document.createElement('a');
    element.href = URL.createObjectURL(new Blob([text], { type: 'text/markdown' }));
    element.download = `test-plan-${testPlan.issueId}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  if (error) {
    return (
      <div className="test-plan-error">
        <h3>❌ Error</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="test-plan-loading">
        <div className="spinner"></div>
        <p>Generating test plan...</p>
      </div>
    );
  }

  if (!testPlan) {
    return null;
  }

  return (
    <div className="test-plan-display">
      <div className="test-plan-header">
        <h2>📋 Test Plan: {testPlan.issueId}</h2>
        <p className="generated-at">Generated: {new Date(testPlan.generatedAt).toLocaleString()}</p>
      </div>

      <div className="test-cases">
        {testPlan.testCases.map((tc, idx) => (
          <div key={idx} className="test-case">
            <div className="test-case-header">
              <span className="tc-id">{tc.id}</span>
              <h4 className="tc-title">{tc.title}</h4>
              <span className={`priority priority-${tc.priority.toLowerCase()}`}>
                {tc.priority}
              </span>
            </div>

            <div className="test-case-steps">
              <h5>Steps:</h5>
              <ol>
                {tc.steps.map((step, stepIdx) => (
                  <li key={stepIdx}>{step}</li>
                ))}
              </ol>
            </div>

            <div className="test-case-expected">
              <h5>Expected Result:</h5>
              <p>{tc.expectedResult}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="test-plan-actions">
        <button onClick={copyToClipboard} className="btn btn-action">
          📋 Copy to Clipboard
        </button>
        <button onClick={downloadAsJson} className="btn btn-action">
          💾 Download JSON
        </button>
        <button onClick={downloadAsMarkdown} className="btn btn-action">
          📄 Download Markdown
        </button>
      </div>
    </div>
  );
};

const formatTestPlanAsText = (testPlan) => {
  let text = `Test Plan: ${testPlan.issueId}\nGenerated: ${testPlan.generatedAt}\n\n`;
  testPlan.testCases.forEach((tc) => {
    text += `\n${tc.id}: ${tc.title} [${tc.priority}]\n`;
    text += 'Steps:\n';
    tc.steps.forEach((step) => {
      text += `  - ${step}\n`;
    });
    text += `Expected: ${tc.expectedResult}\n`;
  });
  return text;
};

const formatTestPlanAsMarkdown = (testPlan) => {
  let md = `# Test Plan: ${testPlan.issueId}\n\n**Generated:** ${testPlan.generatedAt}\n\n`;
  testPlan.testCases.forEach((tc) => {
    md += `## ${tc.id}: ${tc.title}\n\n`;
    md += `**Priority:** ${tc.priority}\n\n`;
    md += `### Steps\n\n`;
    tc.steps.forEach((step, idx) => {
      md += `${idx + 1}. ${step}\n`;
    });
    md += `\n### Expected Result\n\n${tc.expectedResult}\n\n`;
    md += '---\n\n';
  });
  return md;
};

export default TestPlanDisplay;
