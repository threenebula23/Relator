"""Build coverage summary Markdown from coverage.json-style payload."""

from __future__ import annotations

import json
from pathlib import Path

from relator import Template


def main() -> None:
    here = Path(__file__).resolve().parent
    data = json.loads((here / "sample_coverage.json").read_text(encoding="utf-8"))
    totals = data["totals"]
    metrics = [
        {
            "metric": "percent_covered",
            "value": str(totals.get("percent_covered", "")),
        },
        {
            "metric": "covered_lines",
            "value": str(totals.get("covered_lines", "")),
        },
        {
            "metric": "num_statements",
            "value": str(totals.get("num_statements", "")),
        },
    ]
    low_files: list[dict[str, str]] = []
    for path, info in (data.get("files") or {}).items():
        pct = float((info.get("summary") or {}).get("percent_covered") or 0)
        if pct < 80.0:
            low_files.append({"file": path, "percent_covered": str(pct)})

    t = Template(here / "template.md")
    t.data(["metrics", metrics])
    t.data(["low_files", low_files])

    out_dir = here / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "coverage_report.md"
    t.compile(out_path)
    print("Written:", out_path)


if __name__ == "__main__":
    main()
