import json
from src.core.llm import get_llm
from src.core.vector_store import QdrantStore
from src.core.document_loader import load_documents, chunk_text


class DocumentAnalyzerAgent:
    def __init__(self):
        self.llm = get_llm()
        self.store = QdrantStore()

    def ingest(self, data_dir: str) -> int:
        docs = load_documents(data_dir)
        if not docs:
            return 0

        chunked = []
        for doc in docs:
            chunks = chunk_text(doc["content"])
            for i, chunk in enumerate(chunks):
                chunked.append({
                    "content": chunk,
                    "source": doc["source"],
                    "doc_type": doc["doc_type"],
                    "metadata": {**doc["metadata"], "chunk_index": i},
                })

        return self.store.add_documents(chunked)

    def extract_requirements(self, query: str = "") -> list[dict]:
        search_query = query or "extract all features, user stories, acceptance criteria, functional requirements, non-functional requirements, constraints, edge cases"
        results = self.store.search(search_query, top_k=15)

        context = "\n\n".join(r["doc"] for r in results)

        prompt = f"""You are a senior QA analyst. Analyze the following project documentation and extract all requirements.

Extract and categorize:
1. Features (list each feature with description)
2. User Stories (As a [role], I want [goal], so that [reason])
3. Acceptance Criteria (specific, testable conditions)
4. Functional Requirements
5. Non-Functional Requirements (performance, security, usability)
6. Edge Cases & Constraints

Output as JSON with this structure:
{{
  "features": [{{"name": "...", "description": "..."}}],
  "user_stories": [{{"role": "...", "goal": "...", "reason": "..."}}],
  "acceptance_criteria": [{{"feature": "...", "criterion": "..."}}],
  "functional_requirements": ["..."],
  "non_functional_requirements": ["..."],
  "edge_cases": ["..."]
}}

Context:
{context}"""

        response = self.llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("\n```", 1)[0]

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"raw_output": content}

    def analyze_document(self, query: str) -> str:
        results = self.store.search(query, top_k=10)
        context = "\n\n".join(r["doc"] for r in results)

        prompt = f"""Based on the following project documentation, answer the query thoroughly and precisely.

Query: {query}

Context: {context}

Provide a detailed, structured response."""

        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
