from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from relator import Template


def main() -> None:
    here = Path(__file__).resolve().parent
    dist = here / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    assets = here / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.plot([1, 2, 3], [2, 5, 3], marker="o")
    ax.set_title("demo")

    tpl = Template(here / "template.md", assets_dir=assets)
    tpl.data(["product", "relator"])
    tpl.data(["version", "1.2.0"])
    tpl.data(["env", "demo"])
    tpl.data(["lead", "Alice"])
    tpl.slot("ExecutiveSummary", "Кратко: один шаблон, все основные плейсхолдеры и длинный хвост.")
    tpl.data(["snapshot", "SELECT id, name FROM orders WHERE active = 1;"])
    tpl.data(
        [
            "orders",
            [
                {"id": 1, "name": "A", "qty": 2},
                {"id": 2, "name": "B", "qty": 1},
            ],
        ],
    )
    tpl.data(["checklist", ["сборка", "тесты", "релиз"]])
    tpl.data(["phases", ["проектирование", "реализация", "приёмка"]])
    tpl.data(["chart", fig])
    appendix_rows = [{"n": i, "text": f"блок-{i}"} for i in range(1, 243)]
    tpl.data(["appendix_rows", appendix_rows])
    tpl.compile(dist / "full_reference.md")


if __name__ == "__main__":
    main()
