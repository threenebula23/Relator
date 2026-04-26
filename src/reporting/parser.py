"""Parsing helpers for %%len=VAR%% blocks."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import TemplateError


@dataclass
class LenBlock:
    """Parsed loop block metadata.

    Example:
        >>> block = LenBlock("ROWS", 0, 1, 2, "Body")
        >>> block.var_name
        'ROWS'
    """

    var_name: str
    start_line: int
    body_start_line: int
    end_line: int
    body: str


def parse_len_open(line: str) -> str | None:
    """Parse a single len-open line and return variable name.

    Example:
        >>> parse_len_open("%%len=ROWS")
        'ROWS'
        >>> parse_len_open("text")
        None
    """

    stripped = line.strip()
    prefix = "%%len="
    if not stripped.startswith(prefix):
        return None
    var_name = stripped[len(prefix) :].strip()
    if not var_name:
        raise TemplateError("Empty variable name in %%len=...%% block.")
    return var_name


def find_first_len_block(template: str) -> LenBlock | None:
    """Find the first top-level %%len=VAR%% ... %% block.

    Example:
        >>> block = find_first_len_block("%%len=ROWS\\nX\\n%%")
        >>> block.var_name if block else None
        'ROWS'
    """

    lines = template.splitlines(keepends=True)
    start_idx: int | None = None
    body_start_idx: int | None = None
    var_name: str | None = None

    for idx, line in enumerate(lines):
        if start_idx is None:
            parsed = parse_len_open(line)
            if parsed is not None:
                start_idx = idx
                body_start_idx = idx + 1
                var_name = parsed
            continue

        if line.strip() == "%%":
            body = "".join(lines[body_start_idx:idx])
            return LenBlock(
                var_name=var_name or "",
                start_line=start_idx,
                body_start_line=body_start_idx or 0,
                end_line=idx,
                body=body,
            )

    if start_idx is not None:
        raise TemplateError("Unclosed %%len=...%% block.")
    return None

