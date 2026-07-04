import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import pdfParse from 'pdf-parse';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
process.loadEnvFile(path.join(__dirname, '.env'));

const app = express();
app.use(cors());
app.use(express.json());

const PORT = Number(process.env.PORT || 8787);
const COLLECTION_NAME = 'vwo-prd';
const DB_DIR = path.join(__dirname, 'chroma_db');
const DB_FILE = path.join(DB_DIR, `${COLLECTION_NAME}.json`);
const DATA_CANDIDATES = [
  process.env.DATA_DIR ? path.resolve(__dirname, process.env.DATA_DIR) : null,
  path.join(__dirname, 'data', 'data'),
  path.join(__dirname, '..', 'data'),
  path.join(__dirname, '..', 'data', 'data'),
  path.join(__dirname, 'data'),
].filter(Boolean);

const PDF_FILE = DATA_CANDIDATES
  .map((candidate) => ({ candidate, files: fs.existsSync(candidate) ? fs.readdirSync(candidate) : [] }))
  .flatMap(({ candidate, files }) => files.filter((file) => file.toLowerCase().endsWith('.pdf')).map((file) => path.join(candidate, file)))[0] || null;

if (!PDF_FILE) {
  throw new Error('No PDF found in the data folders.');
}

function ensureDb() {
  fs.mkdirSync(DB_DIR, { recursive: true });
  if (!fs.existsSync(DB_FILE)) {
    fs.writeFileSync(DB_FILE, JSON.stringify({ name: COLLECTION_NAME, documents: [], embeddings: [], ids: [] }, null, 2));
  }
}

function loadCollection() {
  ensureDb();
  return JSON.parse(fs.readFileSync(DB_FILE, 'utf8'));
}

function saveCollection(collection) {
  ensureDb();
  fs.writeFileSync(DB_FILE, JSON.stringify(collection, null, 2));
}

function chunkText(text, chunkSize = 800, overlap = 120) {
  const cleaned = text.replace(/\s+/g, ' ').trim();
  if (!cleaned) return [];

  const words = cleaned.split(' ');
  const chunks = [];
  let start = 0;

  while (start < words.length) {
    const end = Math.min(words.length, start + chunkSize);
    const chunk = words.slice(start, end).join(' ');
    if (chunk) chunks.push(chunk);
    if (end === words.length) break;
    start += chunkSize - overlap;
  }

  return chunks;
}

function getTokens(text) {
  return text.toLowerCase().match(/[a-z0-9]+/g) || [];
}

function embedText(text, dimensions = 128) {
  const tokens = getTokens(text);
  const vector = Array.from({ length: dimensions }, () => 0);

  tokens.forEach((token, index) => {
    const hash = Array.from(token).reduce((acc, char) => ((acc * 31) + char.charCodeAt(0)) % 2147483647, 0);
    const position = hash % dimensions;
    vector[position] += 1 / Math.max(1, index + 1);
  });

  const magnitude = Math.sqrt(vector.reduce((acc, value) => acc + value * value, 0)) || 1;
  return vector.map((value) => value / magnitude);
}

function embedTexts(texts) {
  return texts.map((text) => embedText(text));
}

function cosineSimilarity(a, b) {
  let dot = 0;
  let magnitudeA = 0;
  let magnitudeB = 0;
  for (let index = 0; index < a.length; index += 1) {
    dot += a[index] * b[index];
    magnitudeA += a[index] * a[index];
    magnitudeB += b[index] * b[index];
  }
  return dot / (Math.sqrt(magnitudeA) * Math.sqrt(magnitudeB) || 1);
}

async function generateAnswer(question, chunks) {
  if (process.env.GROQ_API_KEY) {
    try {
      const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${process.env.GROQ_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: process.env.GROQ_MODEL || 'openai/gpt-oss-120b',
          messages: [
            { role: 'system', content: 'You answer questions using the provided document context.' },
            { role: 'user', content: `Question: ${question}\n\nContext:\n${chunks.join('\n\n')}` },
          ],
          temperature: 0.2,
          max_tokens: 300,
        }),
      });
      const data = await response.json();
      return data.choices?.[0]?.message?.content || 'No answer returned.';
    } catch (error) {
      return `Local fallback answer: ${chunks[0]?.slice(0, 240) || 'No relevant chunks were found.'}`;
    }
  }

  return chunks.length ? `Based on the retrieved context, the document points to: ${chunks[0].slice(0, 240)}...` : 'No relevant chunks were found.';
}

app.get('/health', (_req, res) => res.json({ status: 'ok' }));

app.post('/ingest', async (_req, res) => {
  try {
    const data = await pdfParse(PDF_FILE);
    const chunks = chunkText(data.text);
    const embeddings = embedTexts(chunks);
    const collection = {
      name: COLLECTION_NAME,
      documents: chunks,
      embeddings,
      ids: chunks.map((_, index) => `chunk-${index}`),
    };
    saveCollection(collection);

    res.json({
      file: path.basename(PDF_FILE),
      chunks: chunks.length,
      collection: COLLECTION_NAME,
      message: 'PDF ingested successfully into the local vector store.',
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/query', async (req, res) => {
  try {
    const { question, top_k = 4 } = req.body;
    const collection = loadCollection();
    const queryEmbedding = embedText(question);
    const scoredChunks = collection.documents
      .map((document, index) => ({
        document,
        score: cosineSimilarity(queryEmbedding, collection.embeddings[index] || embedText(document)),
      }))
      .sort((left, right) => right.score - left.score)
      .slice(0, top_k);

    const chunks = scoredChunks.map((item) => item.document);
    const answer = await generateAnswer(question, chunks);

    res.json({ answer, retrieved_chunks: chunks });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => console.log(`RAG server listening on ${PORT}`));
