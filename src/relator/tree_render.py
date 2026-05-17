from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .errors import TemplateError

_MAX_DEPTH = 200


def _is_branch(value: Any) -> bool:
    """Non-empty mapping = directory with children to walk."""
    return isinstance(value, Mapping) and len(value) > 0


def _sorted_entries(node: Mapping[str, Any], *, dirs_first: bool) -> list[tuple[str, Any]]:
    items = [(str(k), v) for k, v in node.items()]

    def sort_key(item: tuple[str, Any]) -> tuple[Any, ...]:
        name, val = item
        d = 0 if _is_branch(val) else 1
        if dirs_first:
            return (d, name)
        return (name,)

    return sorted(items, key=sort_key)


def _lines_for_mapping(
    node: Mapping[str, Any],
    *,
    dirs_first: bool,
    depth: int,
    seen: set[int],
) -> list[str]:
    if depth > _MAX_DEPTH:
        raise TemplateError('TREE nesting exceeds safe depth limit.')
    lines: list[str] = []
    entries = _sorted_entries(node, dirs_first=dirs_first)
    for i, (name, value) in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = '└── ' if is_last else '├── '
        cont = '    ' if is_last else '│   '
        if _is_branch(value):
            assert isinstance(value, Mapping)
            nid = id(value)
            if nid in seen:
                raise TemplateError('TREE data contains a cycle (repeated dict object).')
            seen.add(nid)
            lines.append(connector + name + '/')
            child_prefix = cont
            child_lines = _lines_for_mapping(value, dirs_first=dirs_first, depth=depth + 1, seen=seen)
            for cl in child_lines:
                lines.append(child_prefix + cl)
            seen.discard(nid)
        else:
            lines.append(connector + name)
    return lines


def render_tree_mapping(
    data: Mapping[str, Any],
    *,
    compact: bool,
    dirs_first: bool,
) -> str:
    if not data:
        return './'
    if len(data) == 1:
        (root_name, root_val), = data.items()
        if _is_branch(root_val):
            assert isinstance(root_val, Mapping)
            seen: set[int] = set()
            nid = id(root_val)
            seen.add(nid)
            parts = [root_name + '/']
            if not compact:
                parts.append('│')
            parts.extend(_lines_for_mapping(root_val, dirs_first=dirs_first, depth=0, seen=seen))
            return '\n'.join(parts)
        return root_name
    seen_root: set[int] = set()
    parts = ['./']
    if not compact:
        parts.append('│')
    parts.extend(_lines_for_mapping(data, dirs_first=dirs_first, depth=0, seen=seen_root))
    return '\n'.join(parts)
