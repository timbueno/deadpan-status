"""Use checked-out monitor state, not GitHub's eventually consistent commit API."""
import json
import re
from pathlib import Path

LABELS = {"up": "🟩 Up", "down": "🟥 Down", "degraded": "🟨 Degraded"}


def reconcile(root):
    summary_path = root / "history/summary.json"
    summary = json.loads(summary_path.read_text())
    readme_path = root / "README.md"
    readme = readme_path.read_text()
    # Validate everything before writing either file.
    for site in summary:
        slug = site["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError("Invalid monitor slug")
        history = (root / "history" / (slug + ".yml")).read_text()
        statuses = re.findall(r"^status: (up|down|degraded)\s*$", history, re.MULTILINE)
        if len(statuses) != 1:
            raise ValueError("Missing or invalid monitor state: " + slug)
        status = statuses[0]
        if site["status"] != status:
            print(slug + ": " + site["status"] + " -> " + status)
        site["status"] = status
        lines = readme.splitlines(keepends=True)
        for index, line in enumerate(lines):
            if line.startswith("|") and "](" + site["url"] + ")" in line:
                lines[index] = re.sub(r"\|\s*[🟩🟥🟨] (?:Up|Down|Degraded)\s*\|",
                                      "| " + LABELS[status] + " |", line, count=1)
        readme = "".join(lines)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    readme_path.write_text(readme)


if __name__ == "__main__":
    reconcile(Path.cwd())
