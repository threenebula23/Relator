from __future__ import annotations
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from .builtins import resolve_cell, resolve_item, resolve_list_namespace, resolve_media_namespace, resolve_table_namespace, resolve_var_special
from .errors import TemplateError
from .parser import find_first_len_block
from .resolver import LoopInfo, resolve_basic_path
PLACEHOLDER_RE = re.compile('\\[\\[([A-Za-z0-9_.]+)\\]\\]')

def _pydantic_mode_from_parts(parts: list[str]) -> str:
    if len(parts) <= 2:
        return ''
    return '_'.join(parts[2:]).upper()

def _orm_mode_from_parts(parts: list[str]) -> str:
    if len(parts) <= 2:
        return ''
    return '_'.join(parts[2:]).upper()

def detect_template_kind(template_path: Path) -> str:
    return 'html' if template_path.suffix.lower() == '.html' else 'md'

def resolve_placeholder(placeholder: str, context_stack: list[Mapping[str, Any]], loop_stack: list[LoopInfo], root_context: Mapping[str, Any], assets_dir: Path, template_kind: str, sql_dialect: str | None=None) -> str:
    parts = placeholder.split('.')
    first = parts[0]
    first_upper = first.upper()
    if first_upper == 'CELL':
        return resolve_cell(parts[1:], loop_stack)
    if first_upper == 'ITEM':
        return resolve_item(loop_stack)
    if first_upper == 'TABLE':
        return resolve_table_namespace(parts[1:], root_context)
    if first_upper in {'LIST', 'ENUM'}:
        return resolve_list_namespace(first_upper, parts[1:], root_context)
    if first_upper == 'MEDIA':
        return resolve_media_namespace(parts[1:], root_context, assets_dir, template_kind)
    if first_upper in {'PYDANTIC', 'SCHEMA'}:
        from .pydantic_render import render_pydantic_fragment
        if len(parts) < 2:
            raise TemplateError(f'{first_upper} requires a variable name, e.g. [[{first_upper}.MyModel]].')
        var_name = parts[1]
        if var_name not in root_context:
            raise TemplateError(f"Unknown variable '{var_name}' for [[{placeholder}]].")
        mode = _pydantic_mode_from_parts(parts)
        return render_pydantic_fragment(root_context[var_name], mode, template_kind)
    if first_upper == 'SQL':
        from .sql_orm import render_sql_fragment
        if len(parts) < 2:
            raise TemplateError('SQL requires a variable name, e.g. [[SQL.query]].')
        var_name = parts[1]
        if var_name not in root_context:
            raise TemplateError(f"Unknown variable '{var_name}' for [[{placeholder}]].")
        return render_sql_fragment(root_context[var_name], template_kind, sql_dialect)
    if first_upper == 'ORM':
        from .sql_orm import render_orm_fragment
        if len(parts) < 2:
            raise TemplateError('ORM requires a variable name, e.g. [[ORM.users.TABLE]].')
        var_name = parts[1]
        if var_name not in root_context:
            raise TemplateError(f"Unknown variable '{var_name}' for [[{placeholder}]].")
        mode = _orm_mode_from_parts(parts)
        return render_orm_fragment(root_context[var_name], mode, template_kind, sql_dialect)
    if len(parts) >= 2:
        special = resolve_var_special(first, parts[1], loop_stack, root_context)
        if special is not None:
            if len(parts) == 2:
                return special
            if parts[1].upper() == 'TABLE':
                return resolve_table_namespace([first, *parts[2:]], root_context)
    value = resolve_basic_path(placeholder, context_stack)
    return str(value)

def replace_placeholders(text: str, context_stack: list[Mapping[str, Any]], loop_stack: list[LoopInfo], root_context: Mapping[str, Any], assets_dir: Path, template_kind: str, sql_dialect: str | None=None) -> str:

    def _sub(match: re.Match[str]) -> str:
        return resolve_placeholder(placeholder=match.group(1), context_stack=context_stack, loop_stack=loop_stack, root_context=root_context, assets_dir=assets_dir, template_kind=template_kind, sql_dialect=sql_dialect)
    return PLACEHOLDER_RE.sub(_sub, text)

def _join_without_linebreaks(lines: list[str]) -> str:
    return ''.join(lines)

def render_template(template: str, root_context: Mapping[str, Any], assets_dir: Path, template_kind: str, context_stack: list[Mapping[str, Any]] | None=None, loop_stack: list[LoopInfo] | None=None, sql_dialect: str | None=None) -> str:
    ctx_stack = context_stack or [root_context]
    loops = loop_stack or []
    block = find_first_len_block(template)
    if block is None:
        return replace_placeholders(template, ctx_stack, loops, root_context, assets_dir, template_kind, sql_dialect)
    lines = template.splitlines(keepends=True)
    prefix = _join_without_linebreaks(lines[:block.start_line])
    suffix = _join_without_linebreaks(lines[block.end_line + 1:])
    if block.var_name not in root_context:
        raise TemplateError(f"Unknown loop variable '{block.var_name}' in %%len=...%% block.")
    seq_raw = root_context[block.var_name]
    if isinstance(seq_raw, (str, bytes)) or not hasattr(seq_raw, '__len__'):
        raise TemplateError(f"Loop variable '{block.var_name}' must be sequence-like.")
    seq = list(seq_raw)
    rendered_body_parts: list[str] = []
    for index, item in enumerate(seq):
        local_scope = {block.var_name: item} if isinstance(item, Mapping) else {block.var_name: item}
        loop = LoopInfo(var_name=block.var_name, seq=seq, index=index)
        rendered_piece = render_template(template=block.body, root_context=root_context, assets_dir=assets_dir, template_kind=template_kind, context_stack=[local_scope, *ctx_stack], loop_stack=[*loops, loop], sql_dialect=sql_dialect)
        rendered_body_parts.append(rendered_piece)
    merged = prefix + ''.join(rendered_body_parts) + suffix
    return render_template(merged, root_context, assets_dir, template_kind, ctx_stack, loops, sql_dialect=sql_dialect)
