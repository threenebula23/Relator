"""Build Markdown test summary from JSON (demo for CI-style reports)."""

from __future__ import annotations

import json
from pathlib import Path

from relator import Template


def main() -> None:
    here = Path(__file__).resolve().parent
    payload = json.loads((here / "sample_pytest.json").read_text(encoding="utf-8"))
    summary_rows = [{k: str(v) for k, v in payload["summary"].items()}]

    t = Template(here / "template.md")
    t.data(["summary", summary_rows])
    t.data(["failed_tests", payload["failed_tests"]])
    t.slot("ci_note", "_Демо: см. `README.md` в этой папке._")

    out_dir = here / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "test_report.md"
    t.compile(out_path)
    print("Written:", out_path)


if __name__ == "__main__":
    main()
