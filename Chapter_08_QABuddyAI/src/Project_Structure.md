# QABuddyAI — Project Structure

## Core (`src/core/`)

| File | Purpose |
|---|---|
| `config.py` | Pydantic-based settings, reads from `.env` |
| `llm.py` | LLM client abstraction (Ollama / OpenAI / Anthropic) |
| `embeddings.py` | **BAAI/bge-m3** embeddings (FP16) + **bge-reranker-v2-m3** reranking via FlagEmbedding |
| `vector_store.py` | Qdrant vector store wrapper — upsert, search, rerank, delete |
| `document_loader.py` | Document ingestion for `.txt`, `.md`, `.pdf`, `.docx` with chunking |

---

## Agents (`src/agents/`)

### 1. Document Analyzer (`document_analyzer.py`)
- RAG pipeline: ingest docs → embed with BGE-m3 → store in Qdrant
- Retrieve with bge-reranker-v2-m3 reranking for precision
- Extract **features**, **user stories**, **acceptance criteria**, **functional/non-functional requirements**, **edge cases**
- Interactive Q&A via `analyze_document(query)`

### 2. Test Case Generator (`test_generator.py`)
- Takes extracted requirements as input
- Applies 6 test design techniques: Equivalence Partitioning, Boundary Value Analysis, Error Guessing, Positive/Negative paths, State Transition
- Outputs structured JSON test cases: Feature → Scenario → Preconditions → Steps → Expected Result → Severity → Priority
- Saves to `data/03_test_cases/`

### 3. Test Executor (`test_executor.py`)
- Generates **Playwright** Python test code from test cases
- Generates **Selenium** Python test code (alternative)
- Dry-run execution with LLM-predicted pass/fail results
- Captures: status, failure reason, duration estimates

### 4. JIRA Integration (`jira_agent.py`)
- Connects to JIRA REST API
- Creates test execution tickets linked to test cases
- Auto-creates **bug tickets** for failed tests with reproduction steps
- Saves ticket tracking to `reports/`

### 5. CI/CD Agent (`cicd_agent.py`)
- Generates **GitHub Actions** workflow YAML (PR, main, scheduled triggers)
- Generates **Jenkinsfile** pipeline (Checkout → Install → Test → Report stages)
- Analyzes Jenkins logs for failures, flaky tests, bottlenecks

### 6. Reporter (`reporter.py`)
- Generates **HTML test report** (Jinja2 template) with summary cards, pass/fail tables, RTM
- **Requirements Traceability Matrix (RTM)**: Source Doc → Requirement → TC ID → Status → JIRA Defect
- JSON summary export

### Orchestrator (`orchestrator.py`)
- Chains all 6 agents into a sequential pipeline with `rich` progress display
- Tracks full state: documents ingested, requirements, test cases, results, report path, JIRA tickets, errors
- Saves pipeline state to JSON for audit

---

## CLI (`src/cli.py`)

Click-based command-line interface.

| Command | Description |
|---|---|
| `python -m cli run` | Run the full pipeline |
| `python -m cli run --push-jira` | Run + push results to JIRA |
| `python -m cli run -f selenium` | Run with Selenium framework |
| `python -m cli ingest` | Only index documents into Qdrant |
| `python -m cli ask -q "query"` | Query the document knowledge base |
| `python -m cli extract` | Extract requirements from documents |
| `python -m cli generate` | Generate test cases |
| `python -m cli generate -f "feature desc"` | Generate tests for a specific feature |
| `python -m cli ui` | Launch the Streamlit web UI |

---

## UI (`src/ui.py`)

Streamlit web application in **light mode** with 5 tabs:

| Tab | Contents |
|---|---|
| 🚀 Pipeline | 7-phase progress tracker, run/reset controls, summary stats, pass/fail donut chart |
| 📋 Test Cases | Full test case browser with search, severity badges, step details in expandable sections |
| 📊 Results | Results table, bar chart of execution times, pass/fail indicators with failure reasons |
| 📝 Reports | Inline HTML report viewer, download button, generated CI/CD YAML previews |
| 💬 Chat | Interactive RAG chat to ask questions about project documents |

---

## Configuration (`.env`)

| Variable | Default | Purpose |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | LLM backend |
| `LLM_MODEL` | `llama3.1` | Model name |
| `EMBED_MODEL` | `BAAI/bge-m3` | Embedding model |
| `RERANK_MODEL` | `BAAI/bge-reranker-v2-m3` | Reranking model |
| `BGE_USE_FP16` | `1` | FP16 acceleration |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant server |
| `QDRANT_COLLECTION` | `qabuddy_docs` | Collection name |
| `JIRA_URL` | — | JIRA instance URL |
| `JIRA_API_TOKEN` | — | JIRA API token |

---

## Data Directory (`src/data/`)

| Directory | Purpose | Sample Files |
|---|---|---|
| `01_selenium_framework/` | Reference Selenium patterns | — |
| `02_playwright_framework/` | Reference Playwright patterns | — |
| `03_test_cases/` | Generated test case output | — |
| `04_jira_tickets/` | JIRA ticket data/cache | — |
| `05_company_docs/` | QA standards, policies | ✅ `qa_standards.md` |
| `06_figma_designs/` | Exported Figma specs | — |
| `07_meeting_notes/` | Meeting transcriptions | ✅ `qa_planning_20260720.md` |
| `08_lucid_charts/` | Flow diagram exports | — |
| `09_prd_srs_brd_frd/` | Requirements documents | ✅ `ecommerce_prd.md`, `ecommerce_srs.md` |
| `10_jenkins_logs/` | CI/CD pipeline logs | — |

---

## Output (`src/reports/`)

| File Pattern | Contents |
|---|---|
| `report_*.html` | Full HTML test report with RTM |
| `summary_*.json` | Numeric summary (total, passed, failed, pass rate) |
| `test_results_*.json` | Raw test execution results |
| `generated_test_*.py` | Generated Playwright/Selenium automation code |
| `pipeline_state_*.json` | Full pipeline state for audit |
| `github_actions.yml` | GitHub Actions CI/CD template |
| `Jenkinsfile` | Jenkins pipeline template |
| `jira_tickets_*.json` | Created JIRA ticket tracking |
