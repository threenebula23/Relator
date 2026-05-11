from __future__ import annotations
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from .errors import TemplateError
from .media import render_media_markup, resolve_media_value
from .resolver import LoopInfo, get_loop_for_var

def ensure_sequence(name: str, value: Any) -> list[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TemplateError(f"Variable '{name}' must be a sequence.")
    return list(value)

def normalize_table_keys(seq: list[Any]) -> list[str]:
    keys: list[str] = []
    for row in seq:
        if not isinstance(row, Mapping):
            continue
        for key in row.keys():
            key_str = str(key)
            if key_str not in keys:
                keys.append(key_str)
    return keys

def format_scalar(value: Any) -> str:
    if value is None:
        return ''
    if isinstance(value, Mapping):
        parts = [f'{k}: {value[k]}' for k in value.keys()]
        return ', '.join(parts)
    return str(value)

def render_table(seq: list[Any], numbered: bool=False, index0: bool=False) -> str:
    keys = normalize_table_keys(seq)
    if not keys:
        return ''
    head_cells = []
    if numbered or index0:
        head_cells.append('#')
    head_cells.extend(keys)
    header = '|' + '|'.join(head_cells) + '|'
    divider = '|' + '|'.join(['---'] * len(head_cells)) + '|'
    rows: list[str] = []
    for i, item in enumerate(seq):
        row_map = item if isinstance(item, Mapping) else {}
        cells: list[str] = []
        if numbered:
            cells.append(str(i + 1))
        elif index0:
            cells.append(str(i))
        cells.extend((format_scalar(row_map.get(k, '')) for k in keys))
        rows.append('|' + '|'.join(cells) + '|')
    return '\n'.join([header, divider, *rows])

def render_list(seq: list[Any], ordered: bool=False) -> str:
    lines: list[str] = []
    for idx, item in enumerate(seq, 1):
        prefix = f'{idx}. ' if ordered else '- '
        lines.append(prefix + format_scalar(item))
    return '\n'.join(lines)

def resolve_cell(path_parts: list[str], loop_stack: list[LoopInfo]) -> str:
    if not loop_stack:
        raise TemplateError('CELL.* is available only inside %%len=VAR%%.')
    current = loop_stack[-1]
    token = path_parts[0].upper() if path_parts else ''
    if token == 'INDEX':
        return str(current.index)
    if token == 'ONE':
        return str(current.index + 1)
    if token == 'COUNT':
        return str(len(current.seq))
    raise TemplateError(f"Unknown CELL token '{token}'.")

def resolve_item(loop_stack: list[LoopInfo]) -> str:
    if not loop_stack:
        raise TemplateError('ITEM is available only inside %%len=VAR%%.')
    current = loop_stack[-1]
    return format_scalar(current.seq[current.index])

def resolve_var_special(var_name: str, token: str, loop_stack: list[LoopInfo], root_context: Mapping[str, Any]) -> str | None:
    token = token.upper()
    loop = get_loop_for_var(loop_stack, var_name)
    seq = ensure_sequence(var_name, root_context.get(var_name, []))
    if token == 'KEYS':
        return '|'.join(normalize_table_keys(seq))
    if token == 'DIVIDER':
        keys = normalize_table_keys(seq)
        return '|'.join(['---'] * len(keys))
    if token == 'VALUES':
        if loop is None:
            raise TemplateError(f'{var_name}.VALUES requires %%len={var_name}%% context.')
        row = seq[loop.index] if loop.index < len(seq) else {}
        keys = normalize_table_keys(seq)
        if isinstance(row, Mapping):
            return '|'.join((format_scalar(row.get(k, '')) for k in keys))
        return format_scalar(row)
    if token == 'TABLE':
        return render_table(seq)
    return None

def resolve_table_namespace(path_parts: list[str], root_context: Mapping[str, Any]) -> str:
    if not path_parts:
        raise TemplateError('TABLE namespace requires variable name.')
    var_name = path_parts[0]
    seq = ensure_sequence(var_name, root_context.get(var_name))
    mode = path_parts[1].upper() if len(path_parts) > 1 else ''
    if mode == 'NUMBERED':
        return render_table(seq, numbered=True)
    if mode == 'INDEX0':
        return render_table(seq, index0=True)
    if mode == 'HTML':
        keys = normalize_table_keys(seq)
        if not keys:
            return ''
        head = ''.join((f'<th>{k}</th>' for k in keys))
        body_rows = []
        for row in seq:
            row_map = row if isinstance(row, Mapping) else {}
            body_rows.append('<tr>' + ''.join((f"<td>{format_scalar(row_map.get(k, ''))}</td>" for k in keys)) + '</tr>')
        return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"
    return render_table(seq)

def resolve_list_namespace(namespace: str, path_parts: list[str], root_context: Mapping[str, Any]) -> str:
    if not path_parts:
        raise TemplateError(f'{namespace} namespace requires variable name.')
    var_name = path_parts[0]
    seq = ensure_sequence(var_name, root_context.get(var_name))
    return render_list(seq, ordered=namespace == 'ENUM')

def resolve_media_namespace(path_parts: list[str], root_context: Mapping[str, Any], assets_dir: Path, template_kind: str) -> str:
    if not path_parts:
        raise TemplateError('MEDIA namespace requires variable name.')
    var_name = path_parts[0]
    value = root_context.get(var_name)
    asset = resolve_media_value(value, assets_dir)
    if asset is None:
        raise TemplateError(f'Unsupported media value for MEDIA.{var_name}.')
    mode = path_parts[1].upper() if len(path_parts) > 1 else ''
    if mode == 'PATH':
        return asset.path.as_posix()
    if mode == 'MD':
        return render_media_markup(asset, 'md', var_name)
    if mode == 'HTML':
        return render_media_markup(asset, 'html', var_name)
    return render_media_markup(asset, template_kind, var_name)
