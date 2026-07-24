import axios from 'axios';

/**
 * API Service Layer
 * Handles all HTTP calls to JIRA and GROQ via backend endpoints or direct calls
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';
const FALLBACK_API_BASE = 'http://localhost:3001/api';

async function postWithFallback(path, payload) {
  try {
    const response = await axios.post(`${API_BASE_URL}${path}`, payload);
    return response.data;
  } catch (error) {
    // if network-related, try fallback mock server once
    const isNetworkError = !error.response;
    if (isNetworkError) {
      try {
        const fallback = await axios.post(`${FALLBACK_API_BASE}${path}`, payload);
        return fallback.data;
      } catch (err) {
        return {
          success: false,
          error: err.response?.data?.error || err.message || 'Failed (fallback)'
        };
      }
    }

    return {
      success: false,
      error: error.response?.data?.error || error.message || 'Request failed'
    };
  }
}

/**
 * Fetch JIRA issue details
 */
export const fetchJiraIssue = async (jiraConfig, issueKey) => {
  try {
    return await postWithFallback('/jira/fetch', {
      baseUrl: jiraConfig?.baseUrl,
      email: jiraConfig?.email,
      token: jiraConfig?.token,
      issueKey
    });
  } catch (error) {
    // network fallback: return a mocked issue so UI can proceed
    if (!error.response) {
      return {
        success: true,
        issue: {
          key: issueKey,
          fields: {
            summary: `Mocked summary for ${issueKey}`,
            description: `This is a mocked description for ${issueKey}. Acceptance criteria: ...`,
            issuetype: { name: 'Story' },
            priority: { name: 'Medium' }
          }
        }
      };
    }

    return {
      success: false,
      error: error.response?.data?.error || error.message || 'Failed to fetch JIRA issue'
    };
  }
};

/**
 * Generate test plan using GROQ
 */
export const generateTestPlan = async (groqConfig, issueData) => {
  try {
    return await postWithFallback('/groq/generate', {
      apiKey: groqConfig?.apiKey,
      model: groqConfig?.model,
      issueData
    });
  } catch (error) {
    // network fallback: locally generate a RICE-POT style strategy
    if (!error.response && issueData) {
      const strategy = [];
      strategy.push({ section: 'Risk & Context', content: `Issue ${issueData.key}: ${issueData.fields.summary}\n${issueData.fields.description}` });
      strategy.push({ section: 'Intent', content: 'Validate core user journeys and edge cases related to the described feature.' });
      strategy.push({ section: 'Core Scenarios', content: '1) Happy path; 2) Authentication/Authorization; 3) Error handling; 4) Data validation' });
      strategy.push({ section: 'Exploratory Focus', content: 'State transitions, boundary values, and performance under small load.' });
      strategy.push({ section: 'Prioritization', content: 'Smoke -> Core scenarios -> Edge cases -> Regression' });

      return {
        success: true,
        testStrategy: { generatedFor: issueData.key, modelUsed: 'local-fallback', strategy }
      };
    }

    return {
      success: false,
      error: error.response?.data?.error || error.message || 'Failed to generate test plan'
    };
  }
};

/**
 * Validate JIRA connection
 */
export const validateJiraConnection = async (jiraConfig) => {
  try {
    return await postWithFallback('/jira/validate', {
      baseUrl: jiraConfig?.baseUrl,
      email: jiraConfig?.email,
      token: jiraConfig?.token
    });
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.error || error.message || 'Connection validation failed'
    };
  }
};

/**
 * Validate GROQ connection
 */
export const validateGroqConnection = async (groqConfig) => {
  try {
    return await postWithFallback('/groq/validate', {
      apiKey: groqConfig?.apiKey,
      model: groqConfig?.model
    });
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.error || error.message || 'GROQ connection failed'
    };
  }
};
