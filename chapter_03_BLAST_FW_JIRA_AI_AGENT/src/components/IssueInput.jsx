import React, { useState } from 'react';

/**
 * IssueInput Component
 * Captures JIRA issue ID and triggers generation
 */
const IssueInput = ({ onGenerate, isLoading }) => {
  const [issueId, setIssueId] = useState('VWO-48');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (issueId.trim()) {
      onGenerate(issueId.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="issue-input-form">
      <div className="input-group">
        <input
          type="text"
          value={issueId}
          onChange={(e) => setIssueId(e.target.value.toUpperCase())}
          placeholder="Enter JIRA Issue ID (e.g., VWO-48)"
          className="issue-input"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !issueId.trim()}
          className="btn btn-generate"
        >
          {isLoading ? 'Generating...' : 'Generate Test Plan'}
        </button>
      </div>
    </form>
  );
};

export default IssueInput;
