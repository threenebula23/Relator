"""CLI entrypoint for reporting package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .template import Template


def build_parser() -> argparse.ArgumentParser:
    """Create argument parser for reporting CLI.

    Example:
        >>> parser = build_parser()
        >>> isinstance(parser, argparse.ArgumentParser)
        True
    """

    parser = argparse.ArgumentParser(description="Compile reporting templates.")
    parser.add_argument("--template", required=True, help="Path to template file.")
    parser.add_argument("--context", required=True, help="Path to JSON context file.")
    parser.add_argument("--output", required=False, help="Output report path.")
    parser.add_argument("--print", dest="print_only", action="store_true", help="Print report to terminal.")
    parser.add_argument("--assets-dir", required=False, help="Directory for generated media files.")
    return parser


def main() -> int:
    """Run CLI command.

    Example:
        >>> # exit_code = main()  # doctest: +SKIP
        >>> True
        True
    """

    parser = build_parser()
    args = parser.parse_args()

    context_path = Path(args.context)
    context = json.loads(context_path.read_text(encoding="utf-8"))
    template = Template(args.template, assets_dir=args.assets_dir)
    for name, value in context.items():
        template.data([name, value])

    if args.print_only:
        template.print()
    if args.output:
        template.compile(args.output)
    return 0

