import os
import csv
import json
import io
from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document as DocxDocument

DATA_SOURCE_DIRS = [
    "01_selenium_framework",
    "02_playwright_framework",
    "03_test_cases",
    "04_jira_tickets",
    "05_company_docs",
    "06_figma_designs",
    "07_meeting_notes",
    "08_lucid_charts",
    "09_prd_srs_brd_frd",
    "10_jenkins_logs",
]

SOURCE_LABELS = {
    "01_selenium_framework": "Selenium Framework",
    "02_playwright_framework": "Playwright Framework",
    "03_test_cases": "Test Cases",
    "04_jira_tickets": "JIRA Tickets",
    "05_company_docs": "Company Docs",
    "06_figma_designs": "Figma Designs",
    "07_meeting_notes": "Meeting Notes",
    "08_lucid_charts": "Lucid Charts",
    "09_prd_srs_brd_frd": "PRD / SRS / BRD / FRD",
    "10_jenkins_logs": "Jenkins Logs",
}


def scan_data_sources(data_dir: str) -> list[dict]:
    results = []
    base = Path(data_dir)

    for folder in DATA_SOURCE_DIRS:
        entry = {
            "folder": folder,
            "label": SOURCE_LABELS.get(folder, folder),
            "status": "missing",
            "files": [],
            "file_count": 0,
            "total_size_bytes": 0,
        }

        folder_path = base / folder
        if not folder_path.exists():
            results.append(entry)
            continue

        all_files = [
            f for f in folder_path.rglob("*")
            if f.is_file()
            and not f.name.startswith(".")
            and f.name != ".gitkeep"
            and not f.name == "Framework link"
        ]

        has_named_file = len(all_files) > 0

        entry["status"] = "available" if has_named_file else "empty"
        entry["file_count"] = len(all_files)
        entry["total_size_bytes"] = sum(f.stat().st_size for f in all_files)
        entry["files"] = [
            {"name": f.name, "size": f.stat().st_size, "ext": f.suffix.lower()}
            for f in all_files
        ]

        if not has_named_file:
            link_file = folder_path / "Framework link"
            if link_file.exists():
                entry["file_count"] = 1
                entry["files"] = [{"name": "Framework link", "size": link_file.stat().st_size, "ext": ""}]
                entry["status"] = "available"

        results.append(entry)

    return results


WILDCARD_EXTS = {".txt", ".md", ".pdf", ".docx", ".csv", ".json", ".xml", ".html", ".htm", ".log", ".py", ".js", ".ts", ".yaml", ".yml", ".feature", "", None}


def _is_ingestable(ext: str) -> bool:
    return ext in WILDCARD_EXTS


def load_documents(data_dir: str) -> list[dict]:
    docs = []
    base = Path(data_dir)

    supported_exts = {
        ".txt": "text", ".md": "markdown", ".pdf": "pdf",
        ".docx": "docx", ".csv": "csv", ".json": "json",
        ".xml": "xml", ".html": "html", ".log": "log",
        ".py": "code", ".js": "code", ".ts": "code",
        ".yaml": "yaml", ".yml": "yaml", ".feature": "gherkin",
    }

    for root, _, files in os.walk(base):
        for fname in files:
            ext = Path(fname).suffix.lower()
            if ext not in supported_exts:
                continue

            fpath = Path(root) / fname
            if fname.startswith(".") or fname == ".gitkeep":
                continue

            try:
                content = _read_file(fpath, ext)
                if content and content.strip():
                    rel_dir = str(Path(root).relative_to(base))
                    docs.append({
                        "content": content,
                        "source": rel_dir,
                        "doc_type": supported_exts[ext],
                        "metadata": {"filename": fname, "path": str(fpath)},
                    })
            except Exception:
                pass

    return docs


def _read_file(fpath: Path, ext: str) -> str:
    try:
        if ext == ".pdf":
            reader = PdfReader(str(fpath))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext == ".docx":
            doc = DocxDocument(str(fpath))
            return "\n".join(p.text for p in doc.paragraphs)
        elif ext == ".csv":
            return fpath.read_text(encoding="utf-8-sig", errors="ignore")
        else:
            return fpath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def parse_csv_test_cases(csv_path: str) -> list[dict]:
    rows = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            tid = row.get("Scenario TID") or row.get("Test Case ID") or f"TC-{i+1:04d}"
            description = row.get("TestCase Description") or row.get("Description") or ""
            steps = row.get("TestSteps") or row.get("Steps to Execute") or ""
            expected = row.get("Expected Result") or ""
            status = row.get("Status") or ""
            precondition = row.get("PreCondition") or ""

            step_list = []
            if steps:
                for j, line in enumerate(steps.replace("\\n", "\n").split("\n")):
                    line = line.strip()
                    if line:
                        step_list.append({"step": j + 1, "action": line, "expected": ""})

            rows.append({
                "tc_id": tid.strip(),
                "feature": description.strip()[:100],
                "scenario": description.strip(),
                "preconditions": [precondition.strip()] if precondition.strip() else [],
                "steps": step_list if step_list else [{"step": 1, "action": description.strip(), "expected": expected.strip()}],
                "severity": "Medium",
                "priority": "P2",
                "test_type": "Functional",
                "technique": "Positive",
                "tags": ["csv-import"],
                "status": status.strip(),
                "expected_result": expected.strip(),
                "generated_at": "",
            })
    return rows


def parse_json_test_cases(json_path: str) -> list[dict]:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ["testCases", "test_cases", "tickets", "issues"]:
            if key in data and isinstance(data[key], list):
                return data[key]
        return list(data.values())[0] if data else []
    return []


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
