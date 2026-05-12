from __future__ import annotations

import json
from pathlib import Path

import pytest

from relator.errors import TemplateError
from relator.template_manifest import build_template_manifest, validate_template_context


def test_manifest_04_agents_template() -> None:
    root = Path(__file__).resolve().parents[1]
    tpl = root / "prototyping" / "example" / "04_agents" / "template.md"
    m = build_template_manifest(tpl)
    assert "tasks" in m["context_keys"]
    assert m["slot_names"] == ["risks", "summary"]
    assert "TABLE.tasks" in m["raw_placeholders"]


def test_validate_ok() -> None:
    root = Path(__file__).resolve().parents[1]
    tpl = root / "prototyping" / "example" / "04_agents" / "template.md"
    ctx = {
        "tasks": [],
        "__slot__summary": "x",
        "__slot__risks": "y",
    }
    validate_template_context(tpl, ctx)


def test_validate_missing_slot() -> None:
    root = Path(__file__).resolve().parents[1]
    tpl = root / "prototyping" / "example" / "04_agents" / "template.md"
    with pytest.raises(TemplateError, match="missing slots"):
        validate_template_context(tpl, {"tasks": [], "__slot__summary": "only"})


def test_validate_missing_context_key() -> None:
    root = Path(__file__).resolve().parents[1]
    tpl = root / "prototyping" / "example" / "04_agents" / "template.md"
    with pytest.raises(TemplateError, match="missing context keys"):
        validate_template_context(tpl, {"__slot__summary": "x", "__slot__risks": "y"})


def test_manifest_json_roundtrip() -> None:
    from relator.template_manifest import manifest_json

    m = json.loads(manifest_json("%%len=rows\n[[ITEM]]\n%%\n[[TABLE.t]]\n@@a@@"))
    assert "rows" in m["context_keys"]
    assert "t" in m["context_keys"]
    assert m["slot_names"] == ["a"]
