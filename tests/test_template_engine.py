"""Integration tests for relator template engine."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from relator import Template


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


def test_slots_replace_after_placeholders(tmp_path: Path) -> None:
    template_text = "Hello [[X]] @@note@@"
    template_path = _write_template(tmp_path, template_text)
    out_path = tmp_path / "report.md"

    t = Template(template_path)
    t.data(["X", "World"])
    t.slot("note", "(see below)")
    t.compile(out_path)

    content = out_path.read_text(encoding="utf-8")
    assert content.strip() == "Hello World (see below)"


def test_template_get_table_keys_pick(tmp_path: Path) -> None:
    template_path = _write_template(tmp_path, "[[TABLE.R]]")
    t = Template(template_path)
    t.data(["R", [{"a": 1, "b": 2}, {"b": 3, "c": 4}]])
    assert t.table_keys("R") == ["a", "b", "c"]
    assert t.pick("R", 0, "a") == 1
    assert t.pick("R", 1, "c") == 4
    assert t.get("R") == [{"a": 1, "b": 2}, {"b": 3, "c": 4}]
    assert t.get("missing", None) is None


def test_slots_from_extra_slot_keys(tmp_path: Path) -> None:
    template_path = _write_template(tmp_path, "@@a@@")
    t = Template(template_path)
    t.render(extra={"__slot__a": "OK"})
    # compile path
    out = tmp_path / "out.md"
    t.compile(out, extra={"__slot__a": "OK"})
    assert out.read_text(encoding="utf-8").strip() == "OK"


def test_compile_template_slot_keys_in_context(tmp_path: Path) -> None:
    from relator import compile_template

    template_path = _write_template(tmp_path, "[[A]]\n@@s@@")
    out = tmp_path / "out.md"
    compile_template(template_path, {"A": 1, "__slot__s": "tail"}, out)
    text = out.read_text(encoding="utf-8")
    assert "1" in text
    assert "tail" in text


def test_print_returns_rendered_text(tmp_path: Path) -> None:
    template_path = _write_template(tmp_path, "Hello [[X]]")
    t = Template(template_path)
    t.data(["X", "World"])
    rendered = t.print(width=60)
    assert "Hello World" in rendered


def test_tree_placeholder(tmp_path: Path) -> None:
    layout = {
        "demo-proj": {
            "README.md": None,
            "docs": {"api.md": None},
            "src": {"main.py": None},
        }
    }
    template_path = _write_template(tmp_path, "[[TREE.layout]]\n---\n[[TREE.layout2.COMPACT]]")
    out_path = tmp_path / "out.md"
    t = Template(template_path)
    t.data(["layout", layout])
    t.data(["layout2", {"a": {"b": None}}])
    t.compile(out_path)
    text = out_path.read_text(encoding="utf-8")
    assert "demo-proj/" in text
    assert "README.md" in text
    assert "docs/" in text
    assert "│" in text


def test_json_placeholder(tmp_path: Path) -> None:
    template_path = _write_template(tmp_path, "[[JSON.cfg]]\n[[JSON.cfg.RAW]]")
    out_path = tmp_path / "out.md"
    t = Template(template_path)
    t.data(["cfg", {"x": 1, "y": [2, 3]}])
    t.compile(out_path)
    text = out_path.read_text(encoding="utf-8")
    assert "```json" in text
    assert '"x": 1' in text
    assert text.count("{") >= 2


def test_render_block_once(tmp_path: Path) -> None:
    template_path = _write_template(
        tmp_path,
        "%%render%%\n[[LIST.items]]\n[[TREE.fs]]\n%%\nfooter",
    )
    out_path = tmp_path / "out.md"
    t = Template(template_path)
    t.data(["items", ["a", "b"]])
    t.data(["fs", {"root": {"f.txt": None}}])
    t.compile(out_path)
    text = out_path.read_text(encoding="utf-8")
    assert "- a" in text
    assert "root/" in text
    assert "footer" in text


def test_compile_save_context_and_inject(tmp_path: Path) -> None:
    template_path = _write_template(tmp_path, "[[title]] [[x]]")
    out1 = tmp_path / "r1.md"
    t = Template(template_path)
    t.data(["title", "T"])
    t.data(["x", 1])
    t.compile(out1, save_context=True)
    ctx_file = tmp_path / "r1.relator-context.json"
    assert ctx_file.is_file()
    tpl2 = _write_template(tmp_path, "[[title]] [[x]] [[y]]")
    t2 = Template(tpl2)
    t2.inject(out1)
    t2.data(["y", 2])
    out2 = tmp_path / "r2.md"
    t2.compile(out2)
    assert out2.read_text(encoding="utf-8").strip() == "T 1 2"


def test_inject_replace(tmp_path: Path) -> None:
    p = tmp_path / "ctx.json"
    p.write_text('{"a": 1}', encoding="utf-8")
    tpl = _write_template(tmp_path, "[[a]]")
    t = Template(tpl)
    t.data(["a", 99])
    t.inject(p, replace=True)
    assert t.render().strip() == "1"

