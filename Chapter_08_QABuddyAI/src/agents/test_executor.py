import json
import time
from datetime import datetime
from pathlib import Path
from src.core.llm import get_llm


class TestExecutorAgent:
    def __init__(self, output_dir: str = "./reports"):
        self.llm = get_llm()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_playwright_code(self, test_cases: list[dict]) -> str:
        tcs_json = json.dumps(test_cases[:5], indent=2)

        prompt = f"""You are a Playwright test automation expert. Generate a complete, runnable Playwright Python test file from these test cases.

Use pytest-playwright format. Include proper fixtures, page objects where appropriate, assertions, and screenshot on failure.

Test Cases:
{tcs_json}

Generate ONLY valid Python code. Use async/await pattern. Include imports."""

        response = self.llm.invoke(prompt)
        code = response.content if hasattr(response, "content") else str(response)
        code = code.strip()
        if code.startswith("```"):
            code = code.split("\n", 1)[1].rsplit("\n```", 1)[0]

        fpath = self.output_dir / f"generated_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        fpath.write_text(code, encoding="utf-8")
        return str(fpath)

    def execute_dry_run(self, test_cases: list[dict]) -> list[dict]:
        """Simulate test execution with LLM-based predictions."""
        results = []

        for tc in test_cases:
            prompt = f"""You are evaluating a test case execution. Based on the test case, predict:
1. Whether it would pass or fail
2. If fail, what the likely failure reason is
3. The expected execution duration in seconds

Test Case:
{json.dumps(tc, indent=2)}

Output as JSON: {{"status": "pass|fail", "failure_reason": "...", "duration_estimate_s": N}}"""

            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, "content") else str(response)
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("\n```", 1)[0]

            try:
                prediction = json.loads(content)
            except json.JSONDecodeError:
                prediction = {"status": "unknown", "failure_reason": "Could not determine", "duration_estimate_s": 0}

            results.append({
                "tc_id": tc.get("tc_id", "UNKNOWN"),
                "scenario": tc.get("scenario", ""),
                "feature": tc.get("feature", ""),
                "status": prediction.get("status", "unknown"),
                "failure_reason": prediction.get("failure_reason", ""),
                "duration_s": prediction.get("duration_estimate_s", 0),
                "executed_at": datetime.now().isoformat(),
                "screenshot": None,
                "logs": [],
            })

        self._save_results(results)
        return results

    def _save_results(self, results: list[dict]):
        fpath = self.output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        fpath.write_text(json.dumps(results, indent=2), encoding="utf-8")

    def generate_selenium_code(self, test_cases: list[dict]) -> str:
        tcs_json = json.dumps(test_cases[:5], indent=2)

        prompt = f"""You are a Selenium test automation expert using Python. Generate a complete, runnable Selenium Python test file.

Use pytest format with selenium webdriver. Include proper setup/teardown, explicit waits, and assertions.

Test Cases:
{tcs_json}

Generate ONLY valid Python code."""

        response = self.llm.invoke(prompt)
        code = response.content if hasattr(response, "content") else str(response)
        code = code.strip()
        if code.startswith("```"):
            code = code.split("\n", 1)[1].rsplit("\n```", 1)[0]

        fpath = self.output_dir / f"generated_test_selenium_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        fpath.write_text(code, encoding="utf-8")
        return str(fpath)
