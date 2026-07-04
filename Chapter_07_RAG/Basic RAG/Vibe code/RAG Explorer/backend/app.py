import os
import json
import re
from pathlib import Path
from typing import List, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader

try:
    import chromadb  # type: ignore
except Exception:  # pragma: no cover - fallback when chromadb cannot be installed
    chromadb = None

try:
    from groq import Groq  # type: ignore
except Exception:  # pragma: no cover - fallback when groq cannot be installed
    Groq = None

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    SentenceTransformer = None

ROOT = Path(__file__).resolve().parent.parent
DATA_CANDIDATES = [
    ROOT / 'data' / 'data',
    ROOT.parent / 'data',
    ROOT.parent / 'data' / 'data',
    ROOT / 'data',
]
DATA_DIR = next((candidate for candidate in DATA_CANDIDATES if candidate.exists()), None)
if DATA_DIR is None:
    raise FileNotFoundError('Could not find the data directory for the PRD PDF.')
PDF_PATH = next(DATA_DIR.glob('*.pdf'))
COLLECTION_NAME = 'vwo-prd'
EMBED_MODEL = 'nomic-ai/nomic-embed-text-v1.5'
GROQ_MODEL = 'openai/gpt-oss-120b'

app = FastAPI(title='RAG Explorer API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if chromadb is None:
    client = None
    collection = None
else:
    client = chromadb.PersistentClient(path=str(ROOT / 'chroma_db'))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
if SentenceTransformer is None:
    embedder = None
else:
    embedder = SentenceTransformer(EMBED_MODEL)
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY', '')) if Groq is not None else None


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    cleaned = re.sub(r'\s+', ' ', text).strip()
    if not cleaned:
        return []
    words = cleaned.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(len(words), start + chunk_size)
        chunk = ' '.join(words[start:end])
        if chunk:
            chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return '\n'.join(page.extract_text() or '' for page in reader.pages)


def ingest_pdf() -> Dict[str, object]:
    text = extract_pdf_text(PDF_PATH)
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail='No chunks could be extracted from the PDF.')

    if embedder is None or collection is None:
        return {
            'file': str(PDF_PATH.name),
            'chunks': len(chunks),
            'collection': COLLECTION_NAME,
            'message': 'PDF text was chunked successfully, but embedding storage is unavailable in this environment.',
        }

    embeddings = embedder.encode(chunks).tolist()
    ids = [f'chunk-{index}' for index in range(len(chunks))]
    collection.upsert(ids=ids, embeddings=embeddings, documents=chunks)

    return {
        'file': str(PDF_PATH.name),
        'chunks': len(chunks),
        'collection': COLLECTION_NAME,
        'message': 'PDF ingested successfully.',
    }


def retrieve_context(question: str, top_k: int = 4) -> List[str]:
    if embedder is None or collection is None:
        return []
    query_embedding = embedder.encode([question])[0].tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    documents = results.get('documents', [[]])[0]
    return documents if documents else []


def generate_answer(question: str, context_chunks: List[str]) -> str:
    if groq_client is None or not getattr(groq_client, 'api_key', None):
        return 'Groq API key is not configured. Please set GROQ_API_KEY to generate a response.'

    prompt = f"""You are a helpful assistant answering questions about a product requirements document.
Use the provided context only.

Question: {question}

Context:
{chr(10).join(context_chunks)}

Answer concisely in a few sentences."""
    chat_completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You answer questions based on the provided document context."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=300,
    )
    return chat_completion.choices[0].message.content


class QueryRequest(BaseModel):
    question: str
    top_k: int = 4


@app.post('/ingest')
def ingest_endpoint() -> Dict[str, object]:
    return ingest_pdf()


@app.post('/query')
def query_endpoint(payload: QueryRequest) -> Dict[str, object]:
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail='A question is required.')
    context_chunks = retrieve_context(payload.question, top_k=payload.top_k)
    answer = generate_answer(payload.question, context_chunks)
    return {
        'answer': answer,
        'retrieved_chunks': context_chunks,
    }


@app.get('/health')
def health() -> Dict[str, str]:
    return {'status': 'ok'}
