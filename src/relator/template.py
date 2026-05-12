from __future__ import annotations
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from rich.console import Console
from rich.markdown import Markdown
from .builtins import ensure_sequence, normalize_table_keys
from .engine import detect_template_kind, render_template
from .errors import TemplateError
from .slots import SLOT_RE, replace_slots
SLOT_KEY_PREFIX = '__slot__'
_MISSING = object()

class Template:

    def __init__(self, template_path: str | Path, assets_dir: str | Path | None=None, sql_dialect: str | None=None):
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise TemplateError(f'Template path does not exist: {self.template_path}')
        self.template_text = self.template_path.read_text(encoding='utf-8')
        self.template_kind = detect_template_kind(self.template_path)
        self._data: dict[str, Any] = {}
        self._slots: dict[str, str] = {}
        self.assets_dir = Path(assets_dir) if assets_dir else Path('assets')
        self.sql_dialect = sql_dialect

    def data(self, pair: list[Any]) -> 'Template':
        if not isinstance(pair, list) or len(pair) != 2:
            raise TemplateError('data(...) expects [name, value].')
        name, value = pair
        if not isinstance(name, str) or not name:
            raise TemplateError('data(...) first item must be non-empty variable name.')
        self._data[name] = value
        return self

    def get(self, name: str, default: Any=_MISSING) -> Any:
        if default is _MISSING:
            if name not in self._data:
                raise TemplateError(f"Unknown variable '{name}' for get(...).")
            return self._data[name]
        return self._data.get(name, default)

    def table_keys(self, var_name: str) -> list[str]:
        if var_name not in self._data:
            raise TemplateError(f"Unknown variable '{var_name}' for table_keys(...).")
        seq = ensure_sequence(var_name, self._data[var_name])
        return normalize_table_keys(seq)

    def pick(self, var_name: str, index: int, key: str) -> Any:
        if var_name not in self._data:
            raise TemplateError(f"Unknown variable '{var_name}' for pick(...).")
        seq = ensure_sequence(var_name, self._data[var_name])
        if index < 0 or index >= len(seq):
            raise TemplateError(f"pick(...): index {index} out of range for '{var_name}' (len={len(seq)}).")
        row = seq[index]
        if not isinstance(row, Mapping):
            raise TemplateError(f"pick(...): row at index {index} of '{var_name}' is not a mapping.")
        if key not in row:
            raise TemplateError(f"pick(...): missing key '{key}' in row {index} of '{var_name}'.")
        return row[key]

    def slot(self, name: str, value: str) -> 'Template':
        if not name or not isinstance(name, str):
            raise TemplateError('slot(...) name must be a non-empty string.')
        self._slots[name] = value if isinstance(value, str) else str(value)
        return self

    def render(self, extra: dict[str, Any] | None=None) -> str:
        merged = dict(self._data)
        slot_map: dict[str, str] = dict(self._slots)
        if extra:
            for key, val in extra.items():
                if isinstance(key, str) and key.startswith(SLOT_KEY_PREFIX):
                    slot_name = key[len(SLOT_KEY_PREFIX):]
                    if slot_name:
                        slot_map[slot_name] = val if isinstance(val, str) else str(val)
                    continue
                merged[key] = val
        body = render_template(template=self.template_text, root_context=merged, assets_dir=self.assets_dir, template_kind=self.template_kind, sql_dialect=self.sql_dialect)
        if SLOT_RE.search(body):
            return replace_slots(body, slot_map)
        return body

    def print(self, extra: dict[str, Any] | None=None, width: int=100) -> str:
        rendered = self.render(extra=extra)
        console = Console(width=width)
        if self.template_kind == 'md':
            console.print(Markdown(rendered))
        else:
            console.print(rendered)
        return rendered

    def compile(self, output_path: str | Path, extra: dict[str, Any] | None=None) -> Path:
        rendered = self.render(extra=extra)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding='utf-8')
        return output

def compile_template(template_path: str | Path, context: dict[str, Any], output_path: str | Path, assets_dir: str | Path | None=None, sql_dialect: str | None=None, extra: dict[str, Any] | None=None) -> Path:
    t = Template(template_path=template_path, assets_dir=assets_dir, sql_dialect=sql_dialect)
    merged_extra: dict[str, Any] = {}
    prefix = SLOT_KEY_PREFIX
    for name, value in context.items():
        if isinstance(name, str) and name.startswith(prefix) and (len(name) > len(prefix)):
            merged_extra[name] = value
        else:
            t.data([name, value])
    if extra:
        merged_extra.update(extra)
    return t.compile(output_path=output_path, extra=merged_extra if merged_extra else None)
