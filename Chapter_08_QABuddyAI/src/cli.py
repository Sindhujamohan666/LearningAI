import click
from pathlib import Path
from src.agents.orchestrator import Orchestrator


@click.group()
def cli():
    """QABuddyAI - Multi-Agent QA Automation Assistant"""
    pass


@cli.command()
@click.option("--project", "-p", default="./data", help="Path to project data directory")
@click.option("--framework", "-f", default="playwright", type=click.Choice(["playwright", "selenium"]))
@click.option("--output", "-o", default="./reports", help="Output directory for reports")
@click.option("--push-jira", is_flag=True, help="Push results to JIRA")
def run(project, framework, output, push_jira):
    """Run the full QABuddyAI pipeline."""
    orch = Orchestrator(
        data_dir=project,
        framework=framework,
        output_dir=output,
        push_jira=push_jira,
    )
    orch.run()


@cli.command()
@click.option("--project", "-p", default="./data", help="Path to project data directory")
def ingest(project):
    """Only ingest documents into Qdrant."""
    from src.agents.document_analyzer import DocumentAnalyzerAgent
    agent = DocumentAnalyzerAgent()
    count = agent.ingest(project)
    print(f"Ingested {count} document chunks into Qdrant.")


@cli.command()
@click.option("--query", "-q", required=True, help="Query about the documents")
def ask(query):
    """Query the document knowledge base."""
    from src.agents.document_analyzer import DocumentAnalyzerAgent
    agent = DocumentAnalyzerAgent()
    response = agent.analyze_document(query)
    print(response)


@cli.command()
@click.option("--project", "-p", default="./data", help="Path to project data directory")
def extract(project):
    """Extract requirements from documents."""
    from src.agents.document_analyzer import DocumentAnalyzerAgent
    import json
    agent = DocumentAnalyzerAgent()
    agent.ingest(project)
    reqs = agent.extract_requirements()
    print(json.dumps(reqs, indent=2))


@cli.command()
@click.option("--feature", "-f", help="Feature description to generate tests for")
@click.option("--project", "-p", default="./data", help="Path to project data directory")
def generate(feature, project):
    """Generate test cases."""
    from src.agents.test_generator import TestGeneratorAgent
    import json
    agent = TestGeneratorAgent()
    if feature:
        tcs = agent.generate_from_query(feature)
    else:
        from src.agents.document_analyzer import DocumentAnalyzerAgent
        doc = DocumentAnalyzerAgent()
        doc.ingest(project)
        reqs = doc.extract_requirements()
        tcs = agent.generate(reqs)
    print(f"Generated {len(tcs)} test cases. Saved to data/03_test_cases/")


@cli.command()
def ui():
    """Launch the Streamlit web UI."""
    import subprocess
    import sys
    ui_path = Path(__file__).parent / "ui.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(ui_path), "--theme.base", "light"])


if __name__ == "__main__":
    cli()
