"""Build a simple data-driven Markdown report."""

from __future__ import annotations

import json
from pathlib import Path

from reporting import Template


def main() -> None:
    here = Path(__file__).resolve().parent
    data = json.loads((here / "data.json").read_text(encoding="utf-8"))

    t = Template(here / "template.md")
    t.data(["title", data["title"]])
    t.data(["kpi", data["kpi"]])
    t.data(["highlights", data["highlights"]])

    out_dir = here / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "business_report.md"
    t.compile(out_path)
    print("Written:", out_path)


if __name__ == "__main__":
    main()
