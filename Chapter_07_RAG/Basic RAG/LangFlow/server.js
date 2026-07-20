import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const envPath = path.join(__dirname, '.env');
const envExamplePath = path.join(__dirname, '.env.example');

if (fs.existsSync(envPath)) {
  process.loadEnvFile(envPath);
  console.log('Loaded environment from .env');
} else if (fs.existsSync(envExamplePath)) {
  process.loadEnvFile(envExamplePath);
  console.log('Loaded environment from .env.example');
}

const app = express();
app.use(cors());
app.use(express.json());

const PORT = Number(process.env.PORT || 8787);
const LANGFLOW_API_KEY = process.env.LANGFLOW_API_KEY || '';
const LANGFLOW_FLOW_ID = process.env.LANGFLOW_FLOW_ID || '';

function extractLangflowText(payload) {
  if (typeof payload === 'string') return payload;
  if (Array.isArray(payload)) {
    return payload.map((entry) => extractLangflowText(entry)).filter(Boolean).join('\n\n');
  }
  if (!payload || typeof payload !== 'object') return '';

  const textKeys = ['text', 'message', 'content', 'answer', 'output', 'result', 'response', 'value'];
  for (const key of textKeys) {
    if (typeof payload[key] === 'string' && payload[key].trim()) return payload[key];
    if (payload[key] && typeof payload[key] === 'object') {
      const nested = extractLangflowText(payload[key]);
      if (nested) return nested;
    }
  }

  for (const value of Object.values(payload)) {
    const nested = extractLangflowText(value);
    if (nested) return nested;
  }

  return '';
}

function parseLangflowOutput(resp) {
  // Prefer structured outputs -> outputs[*].outputs[*].results.message.data.text
  try {
    if (resp && Array.isArray(resp.outputs)) {
      const texts = [];
      for (const out of resp.outputs) {
        if (out && Array.isArray(out.outputs)) {
          for (const inner of out.outputs) {
            try {
              const msg = inner?.results?.message;
              if (msg) {
                // message may be object with data.text or text_key
                const data = msg.data || msg;
                if (typeof data === 'string') {
                  texts.push(data);
                } else if (data && typeof data.text === 'string') {
                  texts.push(data.text);
                } else if (data && typeof data[Object.keys(data)[0]] === 'string') {
                  texts.push(data[Object.keys(data)[0]]);
                }
              }
            } catch (e) {
              // ignore
            }
          }
        }
      }

      const joined = texts.filter(Boolean).join('\n\n').trim();
      if (joined) return maskSensitive(joined);
    }
  } catch (e) {
    // ignore and fallback
  }

  // Fallback to generic extractor but filter out UUIDs and API-like strings
  const raw = extractLangflowText(resp) || '';
  const filtered = raw.split(/\s+/).filter((token) => !isLikelySensitive(token)).join(' ');
  return maskSensitive(filtered) || '';
}

function isLikelySensitive(token) {
  if (!token) return false;
  // simple UUID regex
  const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (uuid.test(token)) return true;
  // API key pattern (simple heuristic)
  if (/^sk-|^pk-|^ak-/.test(token) || token.length > 40 && /[A-Za-z0-9_-]/.test(token)) return true;
  return false;
}

function maskSensitive(text) {
  if (!text) return text;
  const apiKey = process.env.LANGFLOW_API_KEY || '';
  let out = text;
  if (apiKey && typeof apiKey === 'string' && apiKey.trim()) {
    out = out.split(apiKey).join('[REDACTED_API_KEY]');
  }
  // mask UUIDs
  out = out.replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/ig, '[REDACTED_ID]');
  return out;
}

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', service: 'langflow-rag-explorer' });
});

app.post('/api/langflow/run', async (req, res) => {
  try {
    const {
      apiKey,
      flowId,
      question,
      inputValue,
      baseUrl = process.env.LANGFLOW_BASE_URL || 'http://127.0.0.1:7860',
    } = req.body;

    const resolvedApiKey = apiKey || LANGFLOW_API_KEY;
    const resolvedFlowId = flowId || LANGFLOW_FLOW_ID;

    if (!resolvedApiKey || !resolvedFlowId) {
      return res.status(400).json({ error: 'apiKey and flowId are required.' });
    }

    const normalizedBaseUrl = String(baseUrl).replace(/\/$/, '');
    const endpointCandidates = [
      `${normalizedBaseUrl}/api/v1/flows/${encodeURIComponent(resolvedFlowId)}/run`,
      `${normalizedBaseUrl}/api/v1/run/${encodeURIComponent(resolvedFlowId)}`,
    ];

    const payload = {
      input_value: inputValue ?? question ?? '',
      input_type: 'chat',
      output_type: 'chat',
      tweaks: {},
    };

    let lastError = null;

    for (const endpoint of endpointCandidates) {
      try {
        console.log('Proxying to', endpoint, 'using x-api-key present=', Boolean(resolvedApiKey));
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'x-api-key': resolvedApiKey,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });
        const text = await response.text();
        let data = {};
        try {
          data = text ? JSON.parse(text) : {};
        } catch {
          data = { raw: text };
        }

        if (!response.ok) {
          lastError = new Error(`Langflow responded with ${response.status}: ${text}`);
          // try next endpoint
          continue;
        }

        // Parse and sanitize the response to return only user-facing text
        const responseText = parseLangflowOutput(data) || 'The flow returned no readable text.';
        return res.json({
          ok: true,
          endpoint,
          responseText,
        });
      } catch (error) {
        lastError = error;
      }
    }

    return res.status(502).json({
      error: 'Unable to reach the Langflow endpoint.',
      details: lastError?.message || 'Unknown error',
    });
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
});

const DIST_DIR = path.join(__dirname, 'dist');

app.use(express.static(DIST_DIR));
app.get('*', (_req, res) => {
  res.sendFile(path.join(DIST_DIR, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Langflow explorer listening on http://127.0.0.1:${PORT}`);
});
