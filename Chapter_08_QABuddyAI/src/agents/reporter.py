import json
from datetime import datetime
from pathlib import Path
from jinja2 import Template
from src.core.llm import get_llm


REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QABuddyAI - Test Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; color: #1a1a2e; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; }
        .header h1 { font-size: 2rem; font-weight: 700; }
        .header p { opacity: 0.9; margin-top: 0.5rem; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 12px rgba(0,0,0,0.08); text-align: center; }
        .card .number { font-size: 2.5rem; font-weight: 700; }
        .card .label { color: #666; font-size: 0.9rem; margin-top: 0.25rem; }
        .pass { color: #10b981; }
        .fail { color: #ef4444; }
        .total { color: #6366f1; }
        .section { background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
        .section h2 { font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; color: #4f46e5; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #e5e7eb; }
        th { background: #f3f4f6; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; color: #6b7280; }
        .status-pass { color: #10b981; font-weight: 600; }
        .status-fail { color: #ef4444; font-weight: 600; }
        .badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
        .badge-critical { background: #fecaca; color: #991b1b; }
        .badge-high { background: #fed7aa; color: #9a3412; }
        .badge-medium { background: #fef08a; color: #854d0e; }
        .badge-low { background: #d1fae5; color: #065f46; }
        .rtm-table { font-size: 0.85rem; }
        .rtm-table td { max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 QABuddyAI Test Report</h1>
        <p>Generated: {{ generated_at }} | Framework: {{ framework }}</p>
    </div>
    <div class="container">
        <div class="summary-cards">
            <div class="card">
                <div class="number total">{{ summary.total }}</div>
                <div class="label">Total Test Cases</div>
            </div>
            <div class="card">
                <div class="number pass">{{ summary.passed }}</div>
                <div class="label">Passed</div>
            </div>
            <div class="card">
                <div class="number fail">{{ summary.failed }}</div>
                <div class="label">Failed</div>
            </div>
            <div class="card">
                <div class="number">{{ pass_rate }}%</div>
                <div class="label">Pass Rate</div>
            </div>
        </div>

        <div class="section">
            <h2>Test Results</h2>
            <table>
                <thead><tr><th>TC ID</th><th>Feature</th><th>Scenario</th><th>Status</th><th>Duration</th></tr></thead>
                <tbody>
                {% for r in results %}
                <tr>
                    <td>{{ r.tc_id }}</td>
                    <td>{{ r.feature }}</td>
                    <td>{{ r.scenario }}</td>
                    <td class="{% if r.status == 'pass' %}status-pass{% else %}status-fail{% endif %}">{{ r.status.upper() }}</td>
                    <td>{{ r.duration_s }}s</td>
                </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>

        {% if failures %}
        <div class="section">
            <h2>Failures</h2>
            <table>
                <thead><tr><th>TC ID</th><th>Scenario</th><th>Reason</th></tr></thead>
                <tbody>
                {% for f in failures %}
                <tr>
                    <td>{{ f.tc_id }}</td>
                    <td>{{ f.scenario }}</td>
                    <td>{{ f.failure_reason }}</td>
                </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        {% if rtm %}
        <div class="section">
            <h2>Requirements Traceability Matrix (RTM)</h2>
            <table class="rtm-table">
                <thead><tr><th>Requirement</th><th>Source</th><th>TC ID</th><th>Status</th></tr></thead>
                <tbody>
                {% for r in rtm %}
                <tr>
                    <td>{{ r.requirement }}</td>
                    <td>{{ r.source }}</td>
                    <td>{{ r.tc_id }}</td>
                    <td class="{% if r.status == 'pass' %}status-pass{% else %}status-fail{% endif %}">{{ r.status.upper() }}</td>
                </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
    </div>
</body>
</html>"""


class ReporterAgent:
    def __init__(self, output_dir: str = "./reports"):
        self.llm = get_llm()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, test_results: list[dict], requirements: dict = None,
                        framework: str = "playwright") -> str:
        passed = sum(1 for r in test_results if r.get("status") == "pass")
        failed = sum(1 for r in test_results if r.get("status") == "fail")
        total = len(test_results)
        pass_rate = round((passed / total * 100) if total > 0 else 0, 1)

        failures = [r for r in test_results if r.get("status") == "fail"]

        rtm = self._build_rtm(requirements, test_results) if requirements else []

        template = Template(REPORT_TEMPLATE)
        html = template.render(
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            framework=framework,
            summary={"total": total, "passed": passed, "failed": failed},
            pass_rate=pass_rate,
            results=test_results,
            failures=failures,
            rtm=rtm,
        )

        fpath = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fpath.write_text(html, encoding="utf-8")
        return str(fpath)

    def _build_rtm(self, requirements: dict, results: list[dict]) -> list[dict]:
        rtm = []
        features = requirements.get("features", [])
        all_reqs = requirements.get("functional_requirements", [])

        for i, result in enumerate(results):
            req_name = features[i]["name"] if i < len(features) else (all_reqs[i] if i < len(all_reqs) else "N/A")
            rtm.append({
                "requirement": req_name[:80],
                "source": "PRD/SRS",
                "tc_id": result.get("tc_id", ""),
                "status": result.get("status", "unknown"),
            })
        return rtm

    def generate_summary_json(self, results: list[dict]) -> str:
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total": len(results),
            "passed": sum(1 for r in results if r.get("status") == "pass"),
            "failed": sum(1 for r in results if r.get("status") == "fail"),
            "pass_rate": round(
                sum(1 for r in results if r.get("status") == "pass") / len(results) * 100, 1
            ) if results else 0,
        }
        fpath = self.output_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        fpath.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return str(fpath)
