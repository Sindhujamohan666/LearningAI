import json
import httpx
from datetime import datetime
from pathlib import Path
from src.core.config import get_settings
from src.core.llm import get_llm


class JiraAgent:
    def __init__(self):
        self.settings = get_settings()
        self.llm = get_llm()
        self.base_url = self.settings.jira_url.rstrip("/")
        self.auth = (self.settings.jira_email, self.settings.jira_api_token)
        self.project_key = self.settings.jira_project_key

    def create_issue(self, summary: str, description: str, issue_type: str = "Task", labels: list[str] = None) -> dict:
        if not self.base_url:
            return {"error": "JIRA_URL not configured", "summary": summary}

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
            }
        }
        if labels:
            payload["fields"]["labels"] = labels

        try:
            resp = httpx.post(
                f"{self.base_url}/rest/api/2/issue",
                json=payload,
                auth=self.auth,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            if resp.status_code == 201:
                data = resp.json()
                return {"key": data["key"], "url": f"{self.base_url}/browse/{data['key']}"}
            return {"error": resp.text, "status_code": resp.status_code}
        except Exception as e:
            return {"error": str(e)}

    def create_test_tickets(self, test_cases: list[dict]) -> list[dict]:
        results = []
        for tc in test_cases:
            summary = f"[Test] {tc.get('feature', 'Unknown')} - {tc.get('scenario', tc.get('tc_id', 'N/A'))}"
            description = f"""*Test Case ID:* {tc.get('tc_id', 'N/A')}
*Feature:* {tc.get('feature', 'N/A')}
*Scenario:* {tc.get('scenario', 'N/A')}
*Priority:* {tc.get('priority', 'N/A')}
*Severity:* {tc.get('severity', 'N/A')}

*Preconditions:*
{chr(10).join(f'- {p}' for p in tc.get('preconditions', []))}

*Steps:*
{chr(10).join(f'{s.get("step", i+1)}. {s.get("action", "")} → {s.get("expected", "")}' for i, s in enumerate(tc.get('steps', [])))}"""

            result = self.create_issue(summary, description, "Task", ["test-case", "qabuddy"])
            result["tc_id"] = tc.get("tc_id", "N/A")
            results.append(result)

        self._save_results(results)
        return results

    def create_bug_ticket(self, test_result: dict) -> dict:
        summary = f"[Bug] {test_result.get('feature', 'Unknown')} - {test_result.get('scenario', '')}"
        description = f"""*Test Case:* {test_result.get('tc_id', 'N/A')}
*Status:* Failed
*Reason:* {test_result.get('failure_reason', 'Unknown')}
*Executed at:* {test_result.get('executed_at', datetime.now().isoformat())}

*Steps to Reproduce:*
{test_result.get('failure_reason', 'See test case for steps')}"""

        return self.create_issue(summary, description, "Bug", ["bug", "qabuddy"])

    def _save_results(self, results: list[dict]):
        out = Path("./reports")
        out.mkdir(parents=True, exist_ok=True)
        fpath = out / f"jira_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        fpath.write_text(json.dumps(results, indent=2), encoding="utf-8")
