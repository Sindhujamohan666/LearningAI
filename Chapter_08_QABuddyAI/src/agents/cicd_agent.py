import json
from datetime import datetime
from pathlib import Path
from src.core.llm import get_llm


class CICDAgent:
    def __init__(self):
        self.llm = get_llm()

    def generate_github_actions(self, test_framework: str = "playwright") -> str:
        prompt = f"""Generate a complete GitHub Actions workflow YAML for running {test_framework} tests.

Include:
- Triggers: push to main, PR to main, scheduled daily
- Test job with Python setup, dependency install, Playwright browser install
- Test execution step
- Upload test results as artifact
- Post summary as PR comment"""

        response = self.llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("\n```", 1)[0]

        out = Path("./reports")
        out.mkdir(parents=True, exist_ok=True)
        fpath = out / "github_actions.yml"
        fpath.write_text(content, encoding="utf-8")
        return str(fpath)

    def generate_jenkinsfile(self, test_framework: str = "playwright") -> str:
        prompt = f"""Generate a complete Jenkins pipeline (Jenkinsfile) for running {test_framework} tests.

Include:
- Agent configuration
- Stages: Checkout, Install Dependencies, Install Browsers, Run Tests, Publish Reports
- Post-build actions: archive artifacts, publish HTML reports, junit results
- Email notification on failure"""

        response = self.llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("\n```", 1)[0]

        out = Path("./reports")
        out.mkdir(parents=True, exist_ok=True)
        fpath = out / "Jenkinsfile"
        fpath.write_text(content, encoding="utf-8")
        return str(fpath)

    def analyze_jenkins_logs(self, logs_dir: str = "./data/10_jenkins_logs") -> dict:
        log_dir = Path(logs_dir)
        logs = []
        if log_dir.exists():
            for f in log_dir.glob("*.log"):
                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                    logs.append(text[:5000])
                except Exception:
                    pass
            for f in log_dir.glob("*.txt"):
                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                    logs.append(text[:5000])
                except Exception:
                    pass

        if not logs:
            return {"analysis": "No logs found", "recommendations": []}

        combined = "\n---\n".join(logs)
        prompt = f"""Analyze these CI/CD pipeline logs and identify:
1. Failed stages/builds
2. Root causes of failures
3. Flaky tests
4. Performance bottlenecks
5. Recommendations

Logs:
{combined}

Output as JSON with categories."""

        response = self.llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("\n```", 1)[0]

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"analysis": content, "recommendations": []}
