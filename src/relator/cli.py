from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any
from .template import Template
from .template_manifest import build_template_manifest

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Compile or inspect relator templates.')
    parser.add_argument('--template', required=True, help='Path to template file.')
    parser.add_argument('--context', required=False, help='Path to JSON context file (required for compile unless only inspecting).')
    parser.add_argument('--output', required=False, help='Output report path.')
    parser.add_argument('--print', dest='print_only', action='store_true', help='Print report to terminal.')
    parser.add_argument('--assets-dir', required=False, help='Directory for generated media files.')
    parser.add_argument('--inspect', action='store_true', help='Print template manifest JSON to stdout and exit (no --context needed).')
    return parser

def main(argv: list[str] | None=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else None)
    if args.inspect:
        manifest = build_template_manifest(Path(args.template))
        json.dump(manifest, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write('\n')
        return 0
    if not args.context:
        parser.error('--context is required unless --inspect is set.')
    context_path = Path(args.context)
    context = json.loads(context_path.read_text(encoding='utf-8'))
    template = Template(args.template, assets_dir=args.assets_dir)
    prefix = '__slot__'
    merged_extra: dict[str, Any] = {}
    for name, value in context.items():
        if isinstance(name, str) and name.startswith(prefix) and (len(name) > len(prefix)):
            merged_extra[name] = value
        else:
            template.data([name, value])
    extra = merged_extra if merged_extra else None
    if args.print_only:
        template.print(extra=extra)
    if args.output:
        template.compile(args.output, extra=extra)
    if not args.print_only and (not args.output):
        parser.error('Provide --output and/or --print for compile mode.')
    return 0
