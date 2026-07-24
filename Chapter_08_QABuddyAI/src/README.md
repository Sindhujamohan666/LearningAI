# QABuddyAI 🧪

**Multi-Agent AI QA Automation Assistant** — Powered by BGE-m3 embeddings, Qdrant vector store, and LangGraph orchestration.

QABuddyAI ingests your project documentation (PRD, SRS, meeting notes, Figma specs, Lucid charts, JIRA tickets, Jenkins logs), extracts requirements, auto-generates test cases, executes them via Playwright/Selenium, and produces traceability reports with an RTM.

## Architecture

```
Docs → Document Analyzer (RAG) → Test Generator → Test Executor → CI/CD Agent → Reporter → JIRA Agent
         ↑                                                                                    ↓
         └──────────────────────── Workflow Orchestrator ←────────────────────────────────────┘
```

6 specialized AI agents work in a sequential pipeline, orchestrated by a central controller.

## Tech Stack

| Component | Technology |
|---|---|
| **Embeddings** | BAAI/bge-m3 (FP16 mode) |
| **Reranker** | BAAI/bge-reranker-v2-m3 |
| **Vector Store** | Qdrant |
| **LLM Backend** | Ollama / OpenAI / Anthropic |
| **Agent Framework** | LangGraph + LangChain |
| **Test Execution** | Playwright (primary), Selenium |
| **UI** | Streamlit (light mode) |
| **Reporting** | Jinja2 HTML + Plotly charts |

## Quick Start

### Prerequisites

- Python 3.11+
- [Qdrant](https://qdrant.tech/) running on `http://localhost:6333`
- [Ollama](https://ollama.ai/) with a model (e.g., `llama3.1`) or OpenAI API key
- Playwright browsers: `playwright install`

### Installation

```bash
cd src
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
```

### Run the Pipeline

**CLI:**
```bash
cd src
python -m cli run --project ./data --framework playwright
```

**Web UI:**
```bash
cd src
python -m cli ui
```
Opens Streamlit app at `http://localhost:8501`

### CLI Commands

| Command | Description |
|---|---|
| `python -m cli run` | Run full pipeline |
| `python -m cli ingest` | Only index documents into Qdrant |
| `python -m cli ask -q "..."` | Query the knowledge base |
| `python -m cli extract` | Extract requirements from docs |
| `python -m cli generate -f "feature desc"` | Generate test cases |
| `python -m cli ui` | Launch Streamlit UI |

## Data Directory

Place your project documents in `data/`:

| Directory | Contents |
|---|---|
| `01_selenium_framework/` | Reference Selenium code |
| `02_playwright_framework/` | Reference Playwright code |
| `03_test_cases/` | Generated test cases (output) |
| `04_jira_tickets/` | JIRA ticket exports |
| `05_company_docs/` | QA standards, policies |
| `06_figma_designs/` | Exported design specs |
| `07_meeting_notes/` | Meeting transcriptions |
| `08_lucid_charts/` | Flow diagram exports |
| `09_prd_srs_brd_frd/` | **Requirements docs (primary)** |
| `10_jenkins_logs/` | CI/CD pipeline logs |

Supported formats: `.txt`, `.md`, `.pdf`, `.docx`

## Sample Data

Sample e-commerce project documents are included in `src/data/` to demonstrate the pipeline.

## Environment Variables

See `.env.example` for all configuration options. Key variables:

- `QDRANT_URL` — Qdrant server URL
- `EMBED_MODEL=BAAI/bge-m3` — Embedding model
- `RERANK_MODEL=BAAI/bge-reranker-v2-m3` — Reranker model
- `BGE_USE_FP16=1` — FP16 mode for embeddings
- `LLM_PROVIDER=ollama` — LLM backend
- `JIRA_URL`, `JIRA_API_TOKEN` — JIRA integration (optional)

## Output

Reports are saved to `reports/`:
- `report_*.html` — Full HTML test report with RTM
- `summary_*.json` — Summary statistics
- `test_results_*.json` — Raw test results
- `generated_test_*.py` — Generated Playwright/Selenium code
- `github_actions.yml` — CI/CD pipeline template
- `Jenkinsfile` — Jenkins pipeline template
