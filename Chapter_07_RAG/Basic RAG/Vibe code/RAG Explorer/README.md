# RAG Explorer

This project demonstrates a simple end-to-end RAG flow for a VWO PRD PDF. It ingests the document, splits it into chunks, generates simple embeddings locally, stores them in a local JSON-backed vector store, retrieves the most relevant chunks, and shows the answer in a React UI.

## Run locally

1. Install dependencies:
   - `npm install`
2. Start the backend server:
   - `node server.js`
3. In another terminal, start the frontend:
   - `npm run dev`
4. Open the Vite URL, click "Ingest PDF", then ask a question.

If you want a live Groq-generated answer rather than the built-in fallback, set the `GROQ_API_KEY` environment variable before starting the backend.
