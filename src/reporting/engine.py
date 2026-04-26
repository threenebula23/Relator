"""Core render engine for reporting templates."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .builtins import (
    resolve_cell,
    resolve_item,
    resolve_list_namespace,
    resolve_media_namespace,
    resolve_table_namespace,
    resolve_var_special,
)
from .errors import TemplateError
from .parser import find_first_len_block
from .resolver import LoopInfo, resolve_basic_path

PLACEHOLDER_RE = re.compile(r"\[\[([A-Za-z0-9_.]+)\]\]")


def detect_template_kind(template_path: Path) -> str:
    """Detect output kind from template extension.

    Example:
        >>> detect_template_kind(Path("x.html"))
        'html'
    """

    return "html" if template_path.suffix.lower() == ".html" else "md"


def resolve_placeholder(
    placeholder: str,
    context_stack: list[Mapping[str, Any]],
    loop_stack: list[LoopInfo],
    root_context: Mapping[str, Any],
    assets_dir: Path,
    template_kind: str,
) -> str:
    """Resolve a single placeholder string to output text.

    Example:
        >>> resolve_placeholder("CELL.INDEX", [{}], [LoopInfo("A",[1],0)], {"A":[1]}, Path("assets"), "md")
        '0'
    """

    parts = placeholder.split(".")
    first = parts[0]
    first_upper = first.upper()

    if first_upper == "CELL":
        return resolve_cell(parts[1:], loop_stack)
    if first_upper == "ITEM":
        return resolve_item(loop_stack)
    if first_upper == "TABLE":
        return resolve_table_namespace(parts[1:], root_context)
    if first_upper in {"LIST", "ENUM"}:
        return resolve_list_namespace(first_upper, parts[1:], root_context)
    if first_upper == "MEDIA":
        return resolve_media_namespace(parts[1:], root_context, assets_dir, template_kind)

    if len(parts) >= 2:
        special = resolve_var_special(first, parts[1], loop_stack, root_context)
        if special is not None:
            if len(parts) == 2:
                return special
            # Support VAR.TABLE.NUMBERED style.
            if parts[1].upper() == "TABLE":
                return resolve_table_namespace([first, *parts[2:]], root_context)

    value = resolve_basic_path(placeholder, context_stack)
    return str(value)


def replace_placeholders(
    text: str,
    context_stack: list[Mapping[str, Any]],
    loop_stack: list[LoopInfo],
    root_context: Mapping[str, Any],
    assets_dir: Path,
    template_kind: str,
) -> str:
    """Replace all [[...]] placeholders in text.

    Example:
        >>> replace_placeholders("Hello [[X]]", [{"X": "A"}], [], {"X":"A"}, Path("assets"), "md")
        'Hello A'
    """

    def _sub(match: re.Match[str]) -> str:
        return resolve_placeholder(
            placeholder=match.group(1),
            context_stack=context_stack,
            loop_stack=loop_stack,
            root_context=root_context,
            assets_dir=assets_dir,
            template_kind=template_kind,
        )

    return PLACEHOLDER_RE.sub(_sub, text)


def _join_without_linebreaks(lines: list[str]) -> str:
    """Join line list back into template text.

    Example:
        >>> _join_without_linebreaks(["a\\n","b\\n"])
        'a\\nb\\n'
    """

    return "".join(lines)


def render_template(
    template: str,
    root_context: Mapping[str, Any],
    assets_dir: Path,
    template_kind: str,
    context_stack: list[Mapping[str, Any]] | None = None,
    loop_stack: list[LoopInfo] | None = None,
) -> str:
    """Render template text recursively.

    Example:
        >>> tpl = "%%len=ROWS\\n- [[ITEM]]\\n%%"
        >>> render_template(tpl, {"ROWS": ["A"]}, Path("assets"), "md").strip()
        '- A'
    """

    ctx_stack = context_stack or [root_context]
    loops = loop_stack or []

    block = find_first_len_block(template)
    if block is None:
        return replace_placeholders(template, ctx_stack, loops, root_context, assets_dir, template_kind)

    lines = template.splitlines(keepends=True)
    prefix = _join_without_linebreaks(lines[: block.start_line])
    suffix = _join_without_linebreaks(lines[block.end_line + 1 :])

    if block.var_name not in root_context:
        raise TemplateError(f"Unknown loop variable '{block.var_name}' in %%len=...%% block.")

    seq_raw = root_context[block.var_name]
    if isinstance(seq_raw, (str, bytes)) or not hasattr(seq_raw, "__len__"):
        raise TemplateError(f"Loop variable '{block.var_name}' must be sequence-like.")
    seq = list(seq_raw)

    rendered_body_parts: list[str] = []
    for index, item in enumerate(seq):
        local_scope = {block.var_name: item} if isinstance(item, Mapping) else {block.var_name: item}
        loop = LoopInfo(var_name=block.var_name, seq=seq, index=index)
        rendered_piece = render_template(
            template=block.body,
            root_context=root_context,
            assets_dir=assets_dir,
            template_kind=template_kind,
            context_stack=[local_scope, *ctx_stack],
            loop_stack=[*loops, loop],
        )
        rendered_body_parts.append(rendered_piece)

    merged = prefix + "".join(rendered_body_parts) + suffix
    return render_template(merged, root_context, assets_dir, template_kind, ctx_stack, loops)

