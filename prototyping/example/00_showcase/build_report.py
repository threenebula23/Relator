from __future__ import annotations

from pathlib import Path

from PIL import Image

from relator import Template


def main() -> None:
    here = Path(__file__).resolve().parent
    assets = here / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (120, 40), color=(70, 130, 180))

    t = Template(here / "template.md", assets_dir=assets)
    t.data(["project", "demo-app"])
    t.data(["version", "1.0"])
    t.data(
        [
            "items",
            [
                {"sku": "A1", "qty": 3},
                {"sku": "B2", "qty": 1},
            ],
        ]
    )
    t.data(["tags", ["markdown", "ci", "tables"]])
    t.data(["steps", ["Собрать JSON", "Вызвать Template", "Проверить dist/"]])
    t.data(
        [
            "rows",
            [
                {"name": "Alice", "role": "dev"},
                {"name": "Bob", "role": "qa"},
            ],
        ]
    )
    t.data(["logo", img])
    t.slot(
        "intro",
        "Это **Markdown** внутри слота: можно `код`, списки и даже [[псевдо-плейсхолдер]] "
        "без подстановки движком.",
    )

    out_dir = here / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "showcase_report.md"
    t.compile(out_path)
    print("Written:", out_path)


if __name__ == "__main__":
    main()
