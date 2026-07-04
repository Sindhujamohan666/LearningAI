import React, { useState, useEffect } from 'react';
// SettingsPanel removed from main UI — settings are taken from environment/localStorage
import IssueInput from './components/IssueInput';
import TestPlanDisplay from './components/TestPlanDisplay';
import { fetchJiraIssue, generateTestPlan, validateJiraConnection, validateGroqConnection } from './services/api';
import SettingsPanel from './components/SettingsPanel';
import JiraIcon from './assets/jira_icon.svg';
import './App.css';

/**
 * Main App Component
 * Orchestrates settings, issue input, and test plan generation
 */
const App = () => {
  const [settings, setSettings] = useState(null);
  const [testPlan, setTestPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');

  // settings are persisted via localStorage or loaded from VITE_ env at startup
  const [showSettings, setShowSettings] = useState(false);

  const handleSettingsSave = (newSettings) => {
    setSettings(newSettings);
    try {
      localStorage.setItem('appSettings', JSON.stringify(newSettings));
    } catch (e) {}
    setStatusMessage('Settings saved successfully');
    setTimeout(() => setStatusMessage(''), 3000);
  };

  const handleValidateConnection = async (validatingSettings) => {
    setIsLoading(true);
    setError(null);
    setStatusMessage('Validating connections...');

    try {
      // Validate JIRA
      const jiraResult = await validateJiraConnection(validatingSettings.jira);
      if (!jiraResult.success) {
        setError(`JIRA validation failed: ${jiraResult.error}`);
        setIsLoading(false);
        return;
      }

      // Validate GROQ
      const groqResult = await validateGroqConnection(validatingSettings.groq);
      if (!groqResult.success) {
        setError(`GROQ validation failed: ${groqResult.error}`);
        setIsLoading(false);
        return;
      }

      setStatusMessage('All connections validated successfully');
      setTimeout(() => setStatusMessage(''), 3000);
    } catch (err) {
      setError(`Validation error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerate = async (issueId) => {
    // If settings are not present in state, try to build them from VITE env vars
    let effectiveSettings = settings;
    if (!effectiveSettings) {
      effectiveSettings = {
        jira: {
          baseUrl: import.meta.env.VITE_JIRA_BASE_URL || '',
          email: import.meta.env.VITE_JIRA_EMAIL || '',
          token: import.meta.env.VITE_JIRA_API_TOKEN || ''
        },
        groq: {
          apiKey: import.meta.env.VITE_GROQ_API_KEY || '',
          model: import.meta.env.VITE_GROQ_MODEL || 'openai/gpt-oss-120b'
        }
      };
      setSettings(effectiveSettings);
    }

    setIsLoading(true);
    setError(null);
    setTestPlan(null);

    try {
      // Fetch JIRA issue
      setStatusMessage('Fetching JIRA issue...');
      const issueResult = await fetchJiraIssue(effectiveSettings.jira, issueId);
      if (!issueResult.success) {
        setError(`Failed to fetch issue: ${issueResult.error}`);
        setIsLoading(false);
        return;
      }

      // Generate test plan
      setStatusMessage('Generating test plan...');
      const planResult = await generateTestPlan(effectiveSettings.groq, issueResult.issue);
      if (!planResult.success) {
        setError(`Failed to generate test plan: ${planResult.error}`);
        setIsLoading(false);
        return;
      }

      // map API response into TestPlanDisplay shape
      const strategy = planResult.testStrategy || planResult.strategy || [];
      const mapped = {
        issueId: (planResult.testStrategy && planResult.testStrategy.generatedFor) || issueId,
        generatedAt: new Date().toISOString(),
        testCases: (Array.isArray(strategy) ? strategy : []).map((s, idx) => ({
          id: `TS-${idx + 1}`,
          title: s.section || `Section ${idx + 1}`,
          priority: 'Medium',
          steps: [s.content || ''],
          expectedResult: s.content || ''
        }))
      };

      setTestPlan(mapped);
      setStatusMessage('Test plan generated successfully');
      setTimeout(() => setStatusMessage(''), 3000);
    } catch (err) {
      setError(`Generation error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Load saved settings or fall back to VITE env vars and auto-validate if present
    const saved = localStorage.getItem('appSettings');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSettings(parsed);
        return;
      } catch (e) {
        // ignore parse error
      }
    }

    const envBase = import.meta.env.VITE_JIRA_BASE_URL || import.meta.env.VITE_GROQ_API_KEY;
    if (envBase) {
      const envSettings = {
        jira: {
          baseUrl: import.meta.env.VITE_JIRA_BASE_URL || '',
          email: import.meta.env.VITE_JIRA_EMAIL || '',
          token: import.meta.env.VITE_JIRA_API_TOKEN || ''
        },
        groq: {
          apiKey: import.meta.env.VITE_GROQ_API_KEY || '',
          model: import.meta.env.VITE_GROQ_MODEL || 'openai/gpt-oss-120b'
        }
      };
      setSettings(envSettings);
      // Credentials loaded from environment (skip network validation to avoid CORS/local backend issues)
      setStatusMessage('Credentials loaded from environment');
      setTimeout(() => setStatusMessage(''), 3000);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <img src={JiraIcon} alt="JIRA Icon" className="header-icon" />
          <div>
            <h1>JIRA Test Plan Generator</h1>
            <p>AI-powered test planning for JIRA issues</p>
          </div>
        </div>
        <div className="header-right">
          <button className="settings-toggle" onClick={() => setShowSettings(true)}>Settings</button>
        </div>
      </header>

      <SettingsPanel open={showSettings} onClose={() => setShowSettings(false)} onSettingsSave={handleSettingsSave} onValidate={handleValidateConnection} />

      <main className="app-content">
        {/* Settings UI intentionally hidden — using env/localStorage settings */}

        {statusMessage && (
          <div className="status-message">
            {statusMessage}
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        <div className="generator-section">
          <IssueInput 
            onGenerate={handleGenerate}
            isLoading={isLoading}
          />

          <TestPlanDisplay 
            testPlan={testPlan}
            isLoading={isLoading}
            error={error}
          />
        </div>
      </main>

      <footer className="app-footer"></footer>
    </div>
  );
};

export default App;
