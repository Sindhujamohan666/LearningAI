import json
import uuid
from datetime import datetime
from pathlib import Path
from src.core.llm import get_llm


class TestGeneratorAgent:
    def __init__(self, output_dir: str = "./data/03_test_cases"):
        self.llm = get_llm()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, requirements: dict) -> list[dict]:
        reqs_json = json.dumps(requirements, indent=2)

        prompt = f"""You are a senior test architect. Generate comprehensive test cases from the requirements below.

Apply these techniques: Equivalence Partitioning, Boundary Value Analysis, Error Guessing, Positive/Negative paths, State Transition.

Requirements:
{reqs_json}

Generate test cases as JSON array:
[
  {{
    "tc_id": "TC-001",
    "feature": "Feature name",
    "scenario": "Test scenario name",
    "preconditions": ["..."],
    "steps": [
      {{"step": 1, "action": "...", "expected": "..."}}
    ],
    "severity": "Critical|High|Medium|Low",
    "priority": "P0|P1|P2|P3",
    "test_type": "Functional|Integration|E2E|Performance|Security|Usability",
    "technique": "Equivalence Partitioning|Boundary Value|Error Guessing|Positive|Negative|State Transition",
    "tags": ["smoke", "regression"]
  }}
]"""

        response = self.llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("\n```", 1)[0]

        try:
            test_cases = json.loads(content)
        except json.JSONDecodeError:
            return [{"raw_output": content}]

        enriched = []
        for tc in test_cases:
            tc["tc_id"] = tc.get("tc_id", f"TC-{str(uuid.uuid4())[:8].upper()}")
            tc["generated_at"] = datetime.now().isoformat()
            enriched.append(tc)

        self._save(enriched)
        return enriched

    def _save(self, test_cases: list[dict]):
        fpath = self.output_dir / f"test_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        fpath.write_text(json.dumps(test_cases, indent=2), encoding="utf-8")

    def generate_from_query(self, feature_description: str) -> list[dict]:
        reqs = {"features": [{"name": "User Query", "description": feature_description}]}
        return self.generate(reqs)
