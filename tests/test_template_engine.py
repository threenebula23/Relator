"""Integration tests for reporting template engine."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from reporting import Template


def _write_template(tmp_path: Path, body: str, suffix: str = ".md") -> Path:
    path = tmp_path / f"tpl{suffix}"
    path.write_text(body, encoding="utf-8")
    return path


def test_loop_table_and_lists_render(tmp_path: Path) -> None:
    template_text = """%%len=NAME
|[[NAME.KEYS]]|
|---|
|[[NAME.VALUES]]|
line [[CELL.INDEX]]/[[CELL.ONE]]/[[CELL.COUNT]]
%%
[[TABLE.NAME.NUMBERED]]
[[LIST.NAMES]]
[[ENUM.NAMES]]
"""
    template_path = _write_template(tmp_path, template_text)
    out_path = tmp_path / "report.md"

    t = Template(template_path)
    t.data(["NAME", [{"USER": "Ann", "SCORE": 10}, {"USER": "Bob", "SCORE": 20}]])
    t.data(["NAMES", ["Ann", "Bob"]])
    t.compile(out_path)

    content = out_path.read_text(encoding="utf-8")
    assert "|USER|SCORE|" in content
    assert "line 0/1/2" in content
    assert "|#|USER|SCORE|" in content
    assert "- Ann" in content
    assert "1. Ann" in content


def test_media_pil_render(tmp_path: Path) -> None:
    template_text = "[[MEDIA.LOGO]]\n[[MEDIA.LOGO.PATH]]\n[[MEDIA.LOGO.HTML]]"
    template_path = _write_template(tmp_path, template_text)
    out_path = tmp_path / "report.md"
    assets_dir = tmp_path / "assets"

    img = Image.new("RGB", (10, 10), "blue")
    t = Template(template_path, assets_dir=assets_dir)
    t.data(["LOGO", img])
    t.compile(out_path)

    content = out_path.read_text(encoding="utf-8")
    assert "![LOGO](" in content
    assert "<img src=" in content
    assert any(assets_dir.glob("*.png"))


def test_print_returns_rendered_text(tmp_path: Path) -> None:
    template_path = _write_template(tmp_path, "Hello [[X]]")
    t = Template(template_path)
    t.data(["X", "World"])
    rendered = t.print(width=60)
    assert "Hello World" in rendered

