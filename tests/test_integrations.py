"""Tests for Pydantic, SQL, ORM template integrations."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table

from relator import Template
from relator.engine import render_template


pytest.importorskip("pydantic")
pytest.importorskip("sqlalchemy")


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "t.md"
    p.write_text(body, encoding="utf-8")
    return p


def test_pydantic_table_and_json_schema(tmp_path: Path) -> None:
    from pydantic import BaseModel, Field

    class M(BaseModel):
        a: int = Field(description="alpha")
        b: str = "x"

    tpl = "[[PYDANTIC.M.TABLE]]\n[[PYDANTIC.M.JSON_SCHEMA]]"
    out = render_template(tpl, {"M": M}, Path("assets"), "md")
    assert "|field|" in out
    assert "alpha" in out
    assert "```json" in out


def test_schema_alias_matches_pydantic(tmp_path: Path) -> None:
    from pydantic import BaseModel

    class X(BaseModel):
        n: int

    out = render_template("[[SCHEMA.X]]", {"X": X}, Path("assets"), "md")
    assert "X" in out
    assert "n" in out


def test_pydantic_example_fragment() -> None:
    from pydantic import BaseModel, Field

    class Row(BaseModel):
        k: str = Field(examples=["demo"])
        n: int = 1

    out = render_template("[[PYDANTIC.R.EXAMPLE]]", {"R": Row}, Path("assets"), "md")
    assert "```json" in out
    assert "demo" in out
    assert '"n": 1' in out or '"n":' in out


def test_sql_string_fenced(tmp_path: Path) -> None:
    out = render_template("[[SQL.q]]", {"q": "SELECT 1;"}, Path("assets"), "md")
    assert "```sql" in out
    assert "SELECT 1" in out


def test_orm_table_sqlalchemy(tmp_path: Path) -> None:
    md = MetaData()
    t = Table("u", md, Column("id", Integer, primary_key=True), Column("name", String(32)))
    out = render_template("[[ORM.t.TABLE]]\n[[ORM.t.NAME]]", {"t": t}, Path("assets"), "md")
    assert "|column|" in out
    assert "id" in out
    assert out.strip().endswith("u")


def test_orm_ddl_sqlite(tmp_path: Path) -> None:
    md = MetaData()
    t = Table("items", md, Column("id", Integer, primary_key=True))
    out = render_template("[[ORM.t.DDL]]", {"t": t}, Path("assets"), "md", sql_dialect="sqlite")
    assert "CREATE TABLE" in out
    assert "items" in out


def test_template_compile_with_pydantic(tmp_path: Path) -> None:
    from pydantic import BaseModel

    class Row(BaseModel):
        k: str

    path = _write(tmp_path, "[[PYDANTIC.R.TABLE]]")
    out = tmp_path / "o.md"
    tpl = Template(path)
    tpl.data(["R", Row])
    tpl.compile(out)
    assert "|field|" in out.read_text(encoding="utf-8")
