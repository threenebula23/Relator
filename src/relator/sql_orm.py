from __future__ import annotations
from typing import Any
from .errors import TemplateError

def _fenced_sql(body: str, template_kind: str) -> str:
    if template_kind == 'html':
        esc = body.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre><code class="language-sql">{esc}</code></pre>\n'
    return f'```sql\n{body}\n```\n'

def _require_sqlalchemy() -> Any:
    try:
        import sqlalchemy as sa
    except ImportError as exc:  # pragma: no cover
        raise TemplateError("SQL/ORM integration requires: pip install 'relator[sqlalchemy]'") from exc
    return sa

def _sql_text(value: Any, dialect_name: str | None) -> str:
    sa = _require_sqlalchemy()
    if isinstance(value, sa.sql.elements.Executable):
        dialect = _get_dialect(dialect_name)
        compiled = value.compile(dialect=dialect, compile_kwargs={'literal_binds': False})
        return str(compiled)
    return str(value)

def _get_dialect(name: str | None) -> Any:
    sa = _require_sqlalchemy()
    key = (name or 'sqlite').lower()
    if key == 'sqlite':
        from sqlalchemy.dialects import sqlite
        return sqlite.dialect()
    if key == 'postgresql':
        from sqlalchemy.dialects import postgresql
        return postgresql.dialect()
    if key in {'mysql', 'mariadb'}:
        from sqlalchemy.dialects import mysql
        return mysql.dialect()
    raise TemplateError(f"Unsupported sql_dialect '{name}' (try sqlite, postgresql, mysql).")

def render_sql_fragment(value: Any, template_kind: str, dialect_name: str | None) -> str:
    if isinstance(value, str):
        body = value.strip()
        return _fenced_sql(body, template_kind)
    body = _sql_text(value, dialect_name).strip()
    return _fenced_sql(body, template_kind)

def _as_table(value: Any) -> Any:
    sa = _require_sqlalchemy()
    if isinstance(value, sa.Table):
        return value
    tab = getattr(value, '__table__', None)
    if isinstance(tab, sa.Table):
        return tab
    raise TemplateError('ORM.* expects a sqlalchemy.Table or mapped class with __table__.')

def _orm_column_rows(table: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for col in table.columns:
        fk = ''
        for fk_obj in col.foreign_keys:
            fk = f'{fk_obj.target_fullname}'
            break
        rows.append({'column': col.name, 'type': str(col.type), 'nullable': str(col.nullable), 'primary_key': str(col.primary_key), 'foreign_key': fk})
    return rows

def _markdown_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ''
    keys = list(rows[0].keys())
    head = '|' + '|'.join(keys) + '|'
    div = '|' + '|'.join(['---'] * len(keys)) + '|'
    body_lines = []
    for r in rows:
        body_lines.append('|' + '|'.join((str(r.get(k, '')) for k in keys)) + '|')
    return '\n'.join([head, div, *body_lines]) + '\n'

def render_orm_fragment(value: Any, mode: str, template_kind: str, dialect_name: str | None) -> str:
    mode_u = (mode or '').upper()
    table = _as_table(value)
    if mode_u in {'', 'TABLE', 'COLUMNS'}:
        rows = _orm_column_rows(table)
        if template_kind == 'html':
            if not rows:
                return ''
            keys = list(rows[0].keys())
            th = ''.join((f'<th>{k}</th>' for k in keys))
            trs = []
            for r in rows:
                trs.append('<tr>' + ''.join((f"<td>{r.get(k, '')}</td>" for k in keys)) + '</tr>')
            return f"<table><thead><tr>{th}</tr></thead><tbody>{''.join(trs)}</tbody></table>\n"
        return _markdown_table(rows)
    if mode_u == 'NAME':
        return str(table.name)
    if mode_u == 'DDL':
        from sqlalchemy.schema import CreateTable
        dialect = _get_dialect(dialect_name)
        stmt = CreateTable(table)
        body = str(stmt.compile(dialect=dialect))
        return _fenced_sql(body, template_kind)
    raise TemplateError(f"Unknown ORM mode '{mode}'.")
