import { useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8787';

function App() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('Ready to ingest the PDF.');
  const [query, setQuery] = useState('Can you tell me what is there in the document?');
  const [answer, setAnswer] = useState('');
  const [chunks, setChunks] = useState([]);
  const [ingestSummary, setIngestSummary] = useState(null);

  const handleIngest = async () => {
    setLoading(true);
    setStatus('Ingesting PDF and building the vector store...');
    try {
      const response = await fetch(`${API_BASE}/ingest`, { method: 'POST' });
      const data = await response.json();
      setIngestSummary(data);
      setStatus(`Indexed ${data.chunks} chunks from the PDF.`);
    } catch (error) {
      setStatus(`Ingestion failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) {
      setStatus('Please enter a question first.');
      return;
    }

    setLoading(true);
    setStatus('Searching the retrieved context and generating the response...');
    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query, top_k: 4 }),
      });
      const data = await response.json();
      setAnswer(data.answer || 'No answer returned.');
      setChunks(data.retrieved_chunks || []);
      setStatus(`Retrieved ${data.retrieved_chunks?.length || 0} chunks for the query.`);
    } catch (error) {
      setStatus(`Query failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="hero">
        <div className="hero-copy">
          <p className="eyebrow">RAG Explorer</p>
          <h1>Interactive PDF retrieval with local embeddings and ChromaDB.</h1>
          <p className="subtitle">
            Ingest the VWO PRD, split it into chunks, create embeddings, store them locally, retrieve the top 4 passages, and answer your query with Groq.
          </p>
        </div>
      </header>

      <div className="stepper">
        {['PDF', 'Chunk', 'Embed', 'Store', 'Retrieve', 'Answer'].map((step, index) => (
          <div key={step} className="step-item">
            <div className="step-badge">{index + 1}</div>
            <span>{step}</span>
            {index < 5 && <div className="step-line" />}
          </div>
        ))}
      </div>

      <main className="layout-grid">
        <section className="panel inbound-panel">
          <div className="panel-header">
            <div>
              <h2>1 - Ingestion</h2>
              <p className="panel-meta">Load the document, generate embeddings, and store them locally.</p>
            </div>
            <button onClick={handleIngest} disabled={loading}>
              {loading ? 'Ingesting…' : 'Ingest folder'}
            </button>
          </div>

          <div className="ingest-card">
            <div className="ingest-field">
              <label>Source folder</label>
              <p className="ingest-value">{ingestSummary ? 'data folder' : 'data/data/Product Requirements Document_(PRD)_VWO.com.pdf'}</p>
            </div>
            <div className="ingest-field">
              <label>Current file</label>
              <p className="ingest-value">{ingestSummary?.file || 'Product Requirements Document_(PRD)_VWO.com.pdf'}</p>
            </div>
            <div className="ingest-stats">
              <div>
                <span>{ingestSummary?.chunks ?? 0}</span>
                <small>chunks indexed</small>
              </div>
              <div>
                <span>4</span>
                <small>steps</small>
              </div>
              <div>
                <span>1</span>
                <small>collection</small>
              </div>
            </div>
          </div>

          <div className="status-panel">
            <h3>Status</h3>
            <p>{status}</p>
          </div>
        </section>

        <section className="panel query-panel">
          <div className="panel-header">
            <div>
              <h2>2 - Ask the document</h2>
              <p className="panel-meta">Send a query and inspect the top 4 retrieved chunks.</p>
            </div>
          </div>

          <textarea
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            rows={4}
            placeholder="Ask a question about the PRD..."
          />
          <button onClick={handleQuery} disabled={loading} className="query-button">
            {loading ? 'Asking…' : 'Ask'}
          </button>

          <div className="answer-box">
            <div className="answer-label">Answer</div>
            <p>{answer || 'The answer generated from the retrieved document chunks will appear here.'}</p>
          </div>

          <div className="chunk-grid">
            {chunks.length === 0 ? (
              <div className="chunk-empty">No chunks retrieved yet.</div>
            ) : (
              chunks.map((chunk, index) => (
                <article key={`${chunk.slice(0, 20)}-${index}`} className="chunk-card">
                  <div className="chunk-title">Top {index + 1} chunk</div>
                  <p>{chunk}</p>
                </article>
              ))
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
