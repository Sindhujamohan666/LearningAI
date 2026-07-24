import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from src.agents.document_analyzer import DocumentAnalyzerAgent
from src.agents.test_generator import TestGeneratorAgent
from src.agents.test_executor import TestExecutorAgent
from src.agents.jira_agent import JiraAgent
from src.agents.cicd_agent import CICDAgent
from src.agents.reporter import ReporterAgent

console = Console()


class Orchestrator:
    def __init__(self, data_dir: str = "./data", framework: str = "playwright",
                 output_dir: str = "./reports", push_jira: bool = False):
        self.data_dir = data_dir
        self.framework = framework
        self.output_dir = output_dir
        self.push_jira = push_jira
        self.doc_analyzer = DocumentAnalyzerAgent()
        self.test_generator = TestGeneratorAgent(output_dir=f"{data_dir}/03_test_cases")
        self.test_executor = TestExecutorAgent(output_dir=output_dir)
        self.jira_agent = JiraAgent()
        self.cicd_agent = CICDAgent()
        self.reporter = ReporterAgent(output_dir=output_dir)
        self.state = {
            "documents_ingested": 0,
            "requirements": {},
            "test_cases": [],
            "test_results": [],
            "report_path": "",
            "jira_tickets": [],
            "errors": [],
        }

    def run(self) -> dict:
        console.print(Panel.fit("🚀 [bold magenta]QABuddyAI Pipeline Started[/bold magenta]", border_style="magenta"))

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            self._step_ingest(progress)
            self._step_analyze(progress)
            self._step_generate_tests(progress)
            self._step_execute_tests(progress)
            self._step_generate_cicd(progress)
            self._step_report(progress)
            self._step_jira(progress)

        self._print_summary()
        self._save_state()
        return self.state

    def _step_ingest(self, progress):
        task = progress.add_task("[cyan]Phase 1: Ingesting documents into Qdrant (BGE-m3)...", total=None)
        try:
            count = self.doc_analyzer.ingest(self.data_dir)
            self.state["documents_ingested"] = count
            progress.update(task, description=f"[cyan]Phase 1: Ingested {count} chunks into Qdrant")
        except Exception as e:
            self.state["errors"].append(f"Ingest: {e}")
            progress.update(task, description=f"[red]Phase 1: Ingest failed - {e}")

    def _step_analyze(self, progress):
        task = progress.add_task("[cyan]Phase 2: Analyzing documents & extracting requirements...", total=None)
        try:
            reqs = self.doc_analyzer.extract_requirements()
            self.state["requirements"] = reqs
            num_features = len(reqs.get("features", []))
            num_stories = len(reqs.get("user_stories", []))
            progress.update(task, description=f"[cyan]Phase 2: Extracted {num_features} features, {num_stories} user stories")
        except Exception as e:
            self.state["errors"].append(f"Analyze: {e}")
            progress.update(task, description=f"[red]Phase 2: Analysis failed - {e}")

    def _step_generate_tests(self, progress):
        task = progress.add_task("[cyan]Phase 3: Generating test cases...", total=None)
        try:
            tcs = self.test_generator.generate(self.state["requirements"])
            self.state["test_cases"] = tcs
            progress.update(task, description=f"[cyan]Phase 3: Generated {len(tcs)} test cases")
        except Exception as e:
            self.state["errors"].append(f"Test Gen: {e}")
            progress.update(task, description=f"[red]Phase 3: Test generation failed - {e}")

    def _step_execute_tests(self, progress):
        task = progress.add_task("[cyan]Phase 4: Executing tests...", total=None)
        try:
            results = self.test_executor.execute_dry_run(self.state["test_cases"])
            self.state["test_results"] = results

            if self.framework == "playwright":
                self.test_executor.generate_playwright_code(self.state["test_cases"])
            else:
                self.test_executor.generate_selenium_code(self.state["test_cases"])

            passed = sum(1 for r in results if r.get("status") == "pass")
            failed = sum(1 for r in results if r.get("status") == "fail")
            progress.update(task, description=f"[cyan]Phase 4: {passed} passed, {failed} failed")
        except Exception as e:
            self.state["errors"].append(f"Execute: {e}")
            progress.update(task, description=f"[red]Phase 4: Execution failed - {e}")

    def _step_generate_cicd(self, progress):
        task = progress.add_task("[cyan]Phase 5: Generating CI/CD pipelines...", total=None)
        try:
            self.cicd_agent.generate_github_actions(self.framework)
            self.cicd_agent.generate_jenkinsfile(self.framework)
            self.cicd_agent.analyze_jenkins_logs(f"{self.data_dir}/10_jenkins_logs")
            progress.update(task, description="[cyan]Phase 5: Generated GitHub Actions + Jenkinsfile")
        except Exception as e:
            self.state["errors"].append(f"CI/CD: {e}")
            progress.update(task, description=f"[red]Phase 5: CI/CD generation failed - {e}")

    def _step_report(self, progress):
        task = progress.add_task("[cyan]Phase 6: Generating reports & RTM...", total=None)
        try:
            report_path = self.reporter.generate_report(
                self.state["test_results"], self.state["requirements"], self.framework
            )
            self.state["report_path"] = report_path
            progress.update(task, description=f"[cyan]Phase 6: Report saved to {report_path}")
        except Exception as e:
            self.state["errors"].append(f"Report: {e}")
            progress.update(task, description=f"[red]Phase 6: Reporting failed - {e}")

    def _step_jira(self, progress):
        if not self.push_jira:
            progress.add_task("[dim]Phase 7: Skipping JIRA push (use --push-jira to enable)", total=None)
            return
        task = progress.add_task("[cyan]Phase 7: Pushing to JIRA...", total=None)
        try:
            tickets = self.jira_agent.create_test_tickets(self.state["test_cases"])
            self.state["jira_tickets"] = tickets
            created = sum(1 for t in tickets if "key" in t)
            progress.update(task, description=f"[cyan]Phase 7: Created {created} JIRA tickets")
        except Exception as e:
            self.state["errors"].append(f"JIRA: {e}")
            progress.update(task, description=f"[red]Phase 7: JIRA push failed - {e}")

    def _print_summary(self):
        results = self.state["test_results"]
        passed = sum(1 for r in results if r.get("status") == "pass")
        failed = sum(1 for r in results if r.get("status") == "fail")
        total = len(results)

        table = Table(title="📊 Pipeline Summary", border_style="cyan")
        table.add_column("Metric", style="bold")
        table.add_column("Value")

        table.add_row("Documents Ingested", str(self.state["documents_ingested"]))
        table.add_row("Features Extracted", str(len(self.state["requirements"].get("features", []))))
        table.add_row("Test Cases Generated", str(len(self.state["test_cases"])))
        table.add_row("Total Executed", str(total))
        table.add_row("Passed", f"[green]{passed}[/green]")
        table.add_row("Failed", f"[red]{failed}[/red]")
        table.add_row("Pass Rate", f"{round(passed/total*100, 1) if total > 0 else 0}%")
        table.add_row("Report", self.state["report_path"] or "N/A")

        if self.state["errors"]:
            for err in self.state["errors"]:
                table.add_row("Error", f"[red]{err}[/red]")

        console.print(table)

    def _save_state(self):
        out = Path(self.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        state_path = out / f"pipeline_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        saveable = dict(self.state)
        saveable["requirements"] = self.state.get("requirements", {})
        saveable["test_cases"] = self.state.get("test_cases", [])
        saveable["test_results"] = self.state.get("test_results", [])

        state_path.write_text(json.dumps(saveable, indent=2, default=str), encoding="utf-8")
