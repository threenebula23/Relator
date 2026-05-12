from __future__ import annotations
import json
from typing import Any
from .builtins import render_table
from .errors import TemplateError

def _require_pydantic() -> tuple[Any, Any]:
    try:
        from pydantic import BaseModel, TypeAdapter
    except ImportError as exc:  # pragma: no cover
        raise TemplateError("Pydantic integration requires: pip install 'relator[pydantic]'") from exc
    return (BaseModel, TypeAdapter)

def _json_schema_for_value(value: Any) -> tuple[dict[str, Any], str]:
    BaseModel, TypeAdapter = _require_pydantic()
    if isinstance(value, TypeAdapter):
        schema = value.json_schema()
        return (schema, str(schema.get('title', 'Schema')))
    if isinstance(value, type) and issubclass(value, BaseModel):
        schema = value.model_json_schema()
        return (schema, value.__name__)
    if isinstance(value, BaseModel):
        schema = type(value).model_json_schema()
        return (schema, type(value).__name__)
    raise TemplateError('PYDANTIC/SCHEMA expects a BaseModel subclass, instance, or TypeAdapter in context.')

def _schema_property_rows(schema: dict[str, Any]) -> list[dict[str, Any]]:
    props = schema.get('properties') or {}
    required = set(schema.get('required') or [])
    rows: list[dict[str, Any]] = []
    for name, spec in props.items():
        if not isinstance(spec, dict):
            spec = {}
        rows.append({'field': name, 'type': str(spec.get('type', spec.get('anyOf', ''))), 'required': str(name in required), 'default': repr(spec.get('default')) if 'default' in spec else '', 'description': str(spec.get('description', ''))})
    return rows

def _example_from_property_spec(spec: Any) -> Any:
    if not isinstance(spec, dict):
        return None
    if spec.get('examples'):
        return spec['examples'][0]
    if 'example' in spec:
        return spec['example']
    if 'const' in spec:
        return spec['const']
    if spec.get('enum'):
        return spec['enum'][0]
    t = spec.get('type')
    if isinstance(t, list):
        for item in t:
            if item != 'null':
                t = item
                break
    if t == 'string':
        return ''
    if t == 'integer':
        return 0
    if t == 'number':
        return 0.0
    if t == 'boolean':
        return False
    if t == 'array':
        return []
    if t == 'object':
        inner = spec.get('properties') or {}
        return {k: _example_from_property_spec(v) for k, v in inner.items()}
    for key in ('anyOf', 'oneOf'):
        if key in spec:
            for opt in spec[key] or []:
                if isinstance(opt, dict) and opt.get('type') not in (None, 'null'):
                    return _example_from_property_spec(opt)
    return None

def _example_object_from_schema(schema: dict[str, Any]) -> dict[str, Any]:
    props = schema.get('properties') or {}
    return {str(name): _example_from_property_spec(spec) for name, spec in props.items()}

def _fenced_json(body: str, template_kind: str) -> str:
    if template_kind == 'html':
        esc = body.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre><code class="language-json">{esc}</code></pre>\n'
    return f'```json\n{body}\n```\n'

def render_pydantic_fragment(value: Any, mode: str, template_kind: str) -> str:
    _require_pydantic()
    mode_u = (mode or '').upper()
    schema, title = _json_schema_for_value(value)
    if mode_u == 'JSON_SCHEMA':
        body = json.dumps(schema, indent=2, ensure_ascii=False)
        return _fenced_json(body, template_kind)
    if mode_u == 'TABLE':
        rows = _schema_property_rows(schema)
        return render_table(rows) if rows else ''
    if mode_u == 'EXAMPLE':
        example = _example_object_from_schema(schema)
        body = json.dumps(example, indent=2, ensure_ascii=False)
        return _fenced_json(body, template_kind)
    rows = _schema_property_rows(schema)
    keys = list((schema.get('properties') or {}).keys())
    lines = [f"**{title}** — fields: {', '.join(keys)}."] if keys else [f'**{title}**.']
    if rows:
        lines.append('')
        lines.append(render_table(rows))
    return '\n'.join(lines) + ('\n' if rows else '')
