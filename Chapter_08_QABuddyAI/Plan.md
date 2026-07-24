# QABuddyAI — Implementation Plan

## Architecture Overview

QABuddyAI is a **multi-agent AI QA automation assistant** that orchestrates **6 specialized agents** working through a sequence pipeline. It ingests project documentation (PRD, SRS, Figma, JIRA, meeting notes, etc.), auto-generates test cases, executes them via Playwright/Selenium, and produces traceability reports.

### Agent Pipeline

```
Docs Ingest → Document Analysis Agent → Test Case Generator → Test Execution Agent → CI/CD Agent → Reporting Agent → JIRA Integration Agent
                                              ↑                                                                     ↓
                                              └─────────────────── Workflow Orchestrator Agent ←─────────────────────┘
```

---

## Phase 1: Project Scaffolding

- Initialize Python project (recommended for AI/ML ecosystem)
- Set up folder structure mirroring the `data/` directory for input sources
- Choose LLM backend: OpenAI API / Ollama (local) / Claude
- Install core dependencies:
  - `langchain`, `langgraph` (agent orchestration)
  - `qdrant-client` (vector store for RAG)
  - `FlagEmbedding` (BGE-m3 embeddings + BGE-reranker-v2-m3 reranking)
  - `playwright` / `selenium` (test execution)
  - `openai` / `ollama` / `anthropic` (LLM client)
  - `streamlit` (UI)
- Create `.env` for API keys and configuration

## Phase 2: Document Analysis Agent (RAG Pipeline)

- Build a **RAG pipeline** (vector embedding + retrieval) to ingest documents from:
  - `09_prd_srs_brd_frd/` — structured requirement docs (PRD, SRS, BRD, FRD)
  - `06_figma_designs/` — exported design specs or screenshots (multimodal parsing)
  - `07_meeting_notes/` — unstructured text extraction with entity resolution
  - `08_lucid_charts/` — exported flow/process diagrams (image-to-text)
  - `05_company_docs/` — policies, standards, domain context
- Extract: **features**, **user stories**, **acceptance criteria**, **edge cases**, **constraints**
- Embed documents with **BAAI/bge-m3** (FP16 mode), store in **Qdrant**
- Rerank retrieved chunks with **BAAI/bge-reranker-v2-m3** for precision
- Implement hybrid search (semantic + keyword) for accurate retrieval

## Phase 3: Test Case Generator Agent

- Take extracted features/acceptance criteria as input
- Apply test design techniques:
  - Equivalence Partitioning
  - Boundary Value Analysis
  - Error Guessing
  - Positive/Negative path coverage
  - State Transition testing
- Output structured test cases in standard format:
  ```
  Feature → Scenario → Preconditions → Steps → Expected Result → Severity → Priority
  ```
- Store generated test cases in `03_test_cases/` as JSON/YAML
- Generate test case IDs for traceability

## Phase 4: Test Execution Agent

- Convert test cases into executable Playwright/Selenium scripts
- Reference existing framework patterns from `01_selenium_framework/` and `02_playwright_framework/`
- Support both Python and JavaScript/TypeScript code generation
- Execute tests and capture:
  - Pass/Fail status
  - Screenshots on failure
  - Console logs
  - Execution duration
  - Network traces
- Generate defect reports for failures with reproduction steps

## Phase 5: JIRA Integration Agent

- Connect to JIRA REST API
- Read existing tickets from `04_jira_tickets/` for context
- Auto-create test execution tickets linked to generated test cases
- Attach execution results (pass/fail) to corresponding tickets
- Create bug tickets automatically for failed tests with:
  - Summary, description, steps to reproduce
  - Screenshots and logs as attachments
  - Severity based on test case priority
- Link defects to requirements for traceability

## Phase 6: CI/CD Integration Agent

- Read Jenkins logs from `10_jenkins_logs/` for pipeline context
- Generate GitHub Actions workflow YAML templates
- Generate Jenkins pipeline (Jenkinsfile) template
- Support triggers: on PR, on merge to main, scheduled cron, manual dispatch
- Integrate test execution as a CI step
- Post results as PR comments / Slack notifications

## Phase 7: Reporting Agent

- Generate execution summary report (HTML/PDF)
- Generate coverage analysis report:
  - Feature coverage %
  - Requirement coverage %
  - Test pass rate %
  - Defect density
- **Requirements Traceability Matrix (RTM)**:
  ```
  Source Doc → Extracted Requirement → Test Case ID → Test Result → JIRA Defect ID
  ```
- Visual dashboards (charts, graphs) for test metrics

## Phase 8: Workflow Orchestrator Agent

- Central coordinator that chains all agents in sequence
- Workflow:
  ```
  1. Load documents from data/ directories
  2. Run Document Analysis Agent → extract features & requirements
  3. Run Test Case Generator → produce test cases
  4. Run Test Execution Agent → execute tests (or generate code for manual review)
  5. Capture results
  6. Run Reporting Agent → generate reports & RTM
  7. Run JIRA Integration → push results to JIRA
  ```
- CLI interface:
  ```bash
  python -m src.cli --project ./data --framework playwright --llm ollama
  ```
- Streamlit web UI (light mode) for interactive use
- Accept a project input path, run the full pipeline, output final report

---

## Data Directory Mapping

| Directory | Purpose |
|---|---|
| `01_selenium_framework/` | Reference Selenium patterns & best practices |
| `02_playwright_framework/` | Reference Playwright patterns & page objects |
| `03_test_cases/` | Generated test case output (JSON/YAML) |
| `04_jira_tickets/` | JIRA ticket data / local cache |
| `05_company_docs/` | Company policies, standards, domain knowledge |
| `06_figma_designs/` | Exported Figma design specs & screenshots |
| `07_meeting_notes/` | Meeting transcriptions & notes |
| `08_lucid_charts/` | Exported process flow diagrams |
| `09_prd_srs_brd_frd/` | Core requirements documents |
| `10_jenkins_logs/` | CI/CD pipeline logs |

---

## Technology Stack

| Component | Choice | Reason |
|---|---|---|
| Language | Python 3.11+ | Best AI/ML ecosystem |
| LLM Backend | Ollama (local) + OpenAI fallback | Privacy + capability |
| Agent Framework | LangGraph + LangChain | Multi-agent orchestration |
| Vector Store | **Qdrant** | Production-ready, fast, feature-rich |
| Embeddings | **BAAI/bge-m3** (FP16) | SOTA multilingual embeddings |
| Reranker | **BAAI/bge-reranker-v2-m3** | Precision retrieval |
| Test Execution | Playwright (primary), Selenium (fallback) | Modern, cross-browser |
| Reporting | Jinja2 → HTML, Plotly charts | Template-based + interactive |
| UI | **Streamlit (light mode)** | Fast, beautiful prototyping |
| CI/CD | GitHub Actions / Jenkins | Template generation |

---

## Environment Variables

```
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1
LLM_BASE_URL=http://localhost:11434

EMBED_MODEL=BAAI/bge-m3
RERANK_MODEL=BAAI/bge-reranker-v2-m3
BGE_USE_FP16=1

QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=qabuddy_docs

JIRA_URL=
JIRA_EMAIL=
JIRA_API_TOKEN=

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

---

## File Structure

```
Chapter_08_QABuddyAI/
├── Plan.md
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── document_analyzer.py
│   │   ├── test_generator.py
│   │   ├── test_executor.py
│   │   ├── jira_agent.py
│   │   ├── cicd_agent.py
│   │   └── reporter.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── llm.py
│   │   ├── vector_store.py
│   │   ├── embeddings.py
│   │   └── document_loader.py
│   ├── templates/
│   │   ├── report.html.j2
│   │   └── rtm.html.j2
│   ├── cli.py
│   └── ui.py
├── data/
│   ├── 01_selenium_framework/
│   ├── 02_playwright_framework/
│   ├── 03_test_cases/
│   ├── 04_jira_tickets/
│   ├── 05_company_docs/
│   ├── 06_figma_designs/
│   ├── 07_meeting_notes/
│   ├── 08_lucid_charts/
│   ├── 09_prd_srs_brd_frd/
│   └── 10_jenkins_logs/
├── reports/
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```
