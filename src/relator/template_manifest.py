from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from .engine import PLACEHOLDER_RE
from .errors import TemplateError
from .parser import parse_len_open
from .slots import SLOT_RE
__all__ = ['build_template_manifest', 'validate_template_context']

def _context_keys_from_placeholder(placeholder: str) -> set[str]:
    parts = placeholder.split('.')
    if not parts or not parts[0]:
        return set()
    first_upper = parts[0].upper()
    if first_upper in ('CELL', 'ITEM'):
        return set()
    if first_upper in ('TABLE', 'LIST', 'ENUM', 'MEDIA', 'PYDANTIC', 'SCHEMA', 'SQL', 'ORM', 'TREE', 'JSON'):
        return {parts[1]} if len(parts) >= 2 else set()
    if len(parts) >= 2 and parts[1].upper() == 'TABLE':
        return {parts[0]}
    if len(parts) >= 2 and parts[1].upper() in ('KEYS', 'DIVIDER', 'VALUES', 'TABLE'):
        return {parts[0]}
    return {parts[0]}

def _len_loop_vars_in_order(text: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for line in text.splitlines():
        v = parse_len_open(line)
        if v is not None and v not in seen:
            seen.add(v)
            out.append(v)
    return out

def _needs_loop_hint(placeholder: str) -> bool:
    u = placeholder.upper()
    if u.startswith('CELL.') or u == 'ITEM':
        return True
    return '.VALUES' in u

def _read_template_text(template: str | Path) -> str:
    if isinstance(template, Path):
        return template.read_text(encoding='utf-8')
    p = Path(template)
    if p.is_file():
        return p.read_text(encoding='utf-8')
    return template

def build_template_manifest(template: str | Path) -> dict[str, Any]:
    text = _read_template_text(template)
    raw = sorted(set(PLACEHOLDER_RE.findall(text)))
    context_keys: set[str] = set()
    for ph in raw:
        context_keys |= _context_keys_from_placeholder(ph)
    for v in _len_loop_vars_in_order(text):
        context_keys.add(v)
    slot_names = sorted(set(SLOT_RE.findall(text)))
    needs_loop = sorted({p for p in raw if _needs_loop_hint(p)})
    return {'context_keys': sorted(context_keys), 'len_loop_vars': _len_loop_vars_in_order(text), 'slot_names': slot_names, 'raw_placeholders': raw, 'placeholders_requiring_loop': needs_loop}

def validate_template_context(template: str | Path, context: Mapping[str, Any]) -> None:
    manifest = build_template_manifest(template)
    prefix = '__slot__'
    data_keys = {k for k in context if not (isinstance(k, str) and k.startswith(prefix) and (len(k) > len(prefix)))}
    slot_provided = {k[len(prefix):] for k in context if isinstance(k, str) and k.startswith(prefix) and (len(k) > len(prefix))}
    missing_ctx = sorted(set(manifest['context_keys']) - data_keys)
    missing_slots = sorted(set(manifest['slot_names']) - slot_provided)
    if missing_ctx or missing_slots:
        parts: list[str] = []
        if missing_ctx:
            parts.append(f"missing context keys: {', '.join(missing_ctx)}")
        if missing_slots:
            parts.append(f"missing slots (use __slot__name in context or template.slot): {', '.join(missing_slots)}")
        raise TemplateError('; '.join(parts))

def manifest_json(template: str | Path, *, indent: int | None=2) -> str:
    return json.dumps(build_template_manifest(template), indent=indent, ensure_ascii=False)
