"""Combine structured agent JSON with a Markdown template (slots + tables)."""

from __future__ import annotations

import json
from pathlib import Path

from relator import Template


def main() -> None:
    here = Path(__file__).resolve().parent
    data = json.loads((here / "agent_output.json").read_text(encoding="utf-8"))

    t = Template(here / "template.md")
    t.data(["tasks", data["tasks"]])
    t.slot("summary", data.get("summary_md", ""))
    t.slot("risks", data.get("risks_md", ""))

    out_dir = here / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "agent_report.md"
    t.compile(out_path)
    print("Written:", out_path)


if __name__ == "__main__":
    main()
