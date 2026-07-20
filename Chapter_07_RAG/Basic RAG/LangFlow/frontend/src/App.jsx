import { useState } from 'react';

function App() {
  const [question, setQuestion] = useState('Summarize the retrieved context for this document.');
  const [responseText, setResponseText] = useState('');
  const [status, setStatus] = useState('Your configured Langflow flow will respond here.');
  const [loading, setLoading] = useState(false);

  const handleRun = async () => {
    if (!question.trim()) {
      setStatus('Please enter a prompt first.');
      return;
    }

    setLoading(true);
    setStatus('Sending your prompt to Langflow...');

    try {
      const response = await fetch('/api/langflow/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Request failed.');
      }

      setResponseText(data.responseText || 'No readable response returned.');
      setStatus('Response received successfully.');
    } catch (error) {
      setResponseText('');
      setStatus(`Request failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="hero-card">
        <div className="hero-badge">Langflow • RAG Studio</div>
        <h1>Ask your Langflow flow in a polished, distraction-free workspace.</h1>
        <p className="subtitle">
          The interface stays simple, while your configured flow runs in the background using the values from your environment.
        </p>
      </header>

      <main className="workspace-grid">
        <section className="panel prompt-panel">
          <div className="panel-topbar">
            <div>
              <h2>Prompt</h2>
              <p>Type anything you want your flow to answer.</p>
            </div>
            <div className="status-pill">Ready</div>
          </div>

          <textarea value={question} onChange={(event) => setQuestion(event.target.value)} rows={6} />

          <button onClick={handleRun} disabled={loading}>
            {loading ? 'Running…' : 'Run flow'}
          </button>

          <div className="status-box">
            <h3>Status</h3>
            <p>{status}</p>
          </div>
        </section>

        <section className="panel result-panel">
          <div className="panel-topbar">
            <div>
              <h2>Response</h2>
              <p>Your flow output appears here.</p>
            </div>
          </div>

          <div className="result-box">
            {responseText ? <p>{responseText}</p> : <p className="placeholder">The answer will appear here after the flow runs.</p>}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
