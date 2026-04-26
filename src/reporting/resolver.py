"""Placeholder path resolution with context stack."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .errors import TemplateError


@dataclass
class LoopInfo:
    """Loop metadata attached to current scope.

    Example:
        >>> info = LoopInfo("ROWS", [{"a": 1}], 0)
        >>> info.var_name
        'ROWS'
    """

    var_name: str
    seq: list[Any]
    index: int


def resolve_basic_path(path: str, context_stack: list[Mapping[str, Any]]) -> Any:
    """Resolve plain dotted path from stacked contexts.

    Example:
        >>> resolve_basic_path("A.B", [{"A": {"B": 1}}])
        1
    """

    parts = path.split(".")
    root_name = parts[0]

    root = None
    for scope in context_stack:
        if root_name in scope:
            root = scope[root_name]
            break

    if root is None:
        raise TemplateError(f"Unknown placeholder root '{root_name}' for [[{path}]].")

    value = root
    for part in parts[1:]:
        if isinstance(value, Mapping):
            if part not in value:
                raise TemplateError(f"Missing key '{part}' in [[{path}]].")
            value = value[part]
        else:
            if not hasattr(value, part):
                raise TemplateError(f"Cannot access '{part}' in [[{path}]].")
            value = getattr(value, part)
    return value


def get_loop_for_var(loop_stack: list[LoopInfo], var_name: str) -> LoopInfo | None:
    """Find nearest loop by variable name.

    Example:
        >>> loop = LoopInfo("ROWS", [{"A": 1}], 0)
        >>> get_loop_for_var([loop], "ROWS") is not None
        True
    """

    for loop in reversed(loop_stack):
        if loop.var_name == var_name:
            return loop
    return None

