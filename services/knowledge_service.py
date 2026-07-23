
from pathlib import Path

KNOWLEDGE_DIR = Path("knowledge")


def load_file(filename: str) -> str:
    file_path = KNOWLEDGE_DIR / filename

    if not file_path.exists():
        return ""

    return file_path.read_text(encoding="utf-8")


def load_knowledge() -> str:

    files = [
        "system_rules.txt",
        "company_profile.txt",
        "services.txt",
        "lawyers.txt",
        "faqs.txt",
        "contact.txt",
    ]

    content = ""

    for file in files:

        content += "\n\n"

        content += load_file(file)

    return content
