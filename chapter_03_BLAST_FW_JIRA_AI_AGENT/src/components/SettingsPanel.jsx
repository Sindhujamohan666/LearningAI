import React, { useState } from 'react';

/**
 * SettingsPanel Component
 * Captures and stores JIRA and GROQ credentials in localStorage
 */
const SettingsPanel = ({ open = false, onClose = () => {}, onSettingsSave, onValidate }) => {
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('appSettings');
    if (saved) return JSON.parse(saved);
    return {
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
  });

  const [validating, setValidating] = useState(false);

  const handleJiraChange = (e) => {
    const { name, value } = e.target;
    setSettings(prev => ({
      ...prev,
      jira: { ...prev.jira, [name]: value }
    }));
  };

  const handleGroqChange = (e) => {
    const { name, value } = e.target;
    setSettings(prev => ({
      ...prev,
      groq: { ...prev.groq, [name]: value }
    }));
  };

  const handleSave = () => {
    localStorage.setItem('appSettings', JSON.stringify(settings));
    onSettingsSave && onSettingsSave(settings);
    onClose();
  };

  const handleValidate = async () => {
    setValidating(true);
    await onValidate(settings);
    setValidating(false);
  };

  if (!open) return null;

  return (
    <div className="settings-content settings-overlay">
      <h3>Configuration</h3>

      <div className="settings-section">
        <h4>JIRA Configuration</h4>
        <input
          type="text"
          name="baseUrl"
          placeholder="JIRA Base URL (e.g., https://your-jira.atlassian.net)"
          value={settings.jira.baseUrl}
          onChange={handleJiraChange}
          className="setting-input"
        />
        <input
          type="email"
          name="email"
          placeholder="JIRA Email"
          value={settings.jira.email}
          onChange={handleJiraChange}
          className="setting-input"
        />
        <input
          type="password"
          name="token"
          placeholder="JIRA API Token"
          value={settings.jira.token}
          onChange={handleJiraChange}
          className="setting-input"
        />
      </div>

      <div className="settings-section">
        <h4>GROQ Configuration</h4>
        <input
          type="password"
          name="apiKey"
          placeholder="GROQ API Key"
          value={settings.groq.apiKey}
          onChange={handleGroqChange}
          className="setting-input"
        />
        <select
          name="model"
          value={settings.groq.model}
          onChange={handleGroqChange}
          className="setting-input"
        >
          <option value="openai/gpt-oss-120b">openai/gpt-oss-120b (Free)</option>
          <option value="mixtral-8x7b-32768">mixtral-8x7b-32768</option>
        </select>
      </div>

      <div className="settings-actions">
        <button 
          onClick={handleValidate}
          disabled={validating}
          className="btn btn-validate"
        >
          {validating ? 'Validating...' : 'Validate Connection'}
        </button>
        <button 
          onClick={handleSave}
          className="btn btn-save"
        >
          Save Settings
        </button>
        <button 
          onClick={onClose}
          className="btn btn-cancel"
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default SettingsPanel;
