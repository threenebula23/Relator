"""Public Template API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.markdown import Markdown

from .engine import detect_template_kind, render_template
from .errors import TemplateError


class Template:
    """Template object for step-by-step report building.

    Example:
        >>> t = Template("example.md")  # doctest: +SKIP
        >>> t.data(["ROWS", [{"A": 1}]])  # doctest: +SKIP
        >>> t.compile("report.md")  # doctest: +SKIP
    """

    def __init__(self, template_path: str | Path, assets_dir: str | Path | None = None):
        """Load template file.

        Example:
            >>> # t = Template("template.md")
            >>> True
            True
        """

        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise TemplateError(f"Template path does not exist: {self.template_path}")
        self.template_text = self.template_path.read_text(encoding="utf-8")
        self.template_kind = detect_template_kind(self.template_path)
        self._data: dict[str, Any] = {}
        self.assets_dir = Path(assets_dir) if assets_dir else Path("assets")

    def data(self, pair: list[Any]) -> "Template":
        """Set one variable using [name, value] pair.

        Example:
            >>> # t.data(["ROWS", [{"A": 1}]])
            >>> True
            True
        """

        if not isinstance(pair, list) or len(pair) != 2:
            raise TemplateError("data(...) expects [name, value].")
        name, value = pair
        if not isinstance(name, str) or not name:
            raise TemplateError("data(...) first item must be non-empty variable name.")
        self._data[name] = value
        return self

    def render(self, extra: dict[str, Any] | None = None) -> str:
        """Render template to string.

        Example:
            >>> # text = t.render()
            >>> True
            True
        """

        merged = dict(self._data)
        if extra:
            merged.update(extra)
        return render_template(
            template=self.template_text,
            root_context=merged,
            assets_dir=self.assets_dir,
            template_kind=self.template_kind,
        )

    def print(self, extra: dict[str, Any] | None = None, width: int = 100) -> str:
        """Render and print report with rich formatting.

        Example:
            >>> # t.print()
            >>> True
            True
        """

        rendered = self.render(extra=extra)
        console = Console(width=width)
        if self.template_kind == "md":
            console.print(Markdown(rendered))
        else:
            console.print(rendered)
        return rendered

    def compile(self, output_path: str | Path, extra: dict[str, Any] | None = None) -> Path:
        """Render and write report into output file.

        Example:
            >>> # t.compile("report.md")
            >>> True
            True
        """

        rendered = self.render(extra=extra)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        return output


def compile_template(
    template_path: str | Path,
    context: dict[str, Any],
    output_path: str | Path,
    assets_dir: str | Path | None = None,
) -> Path:
    """Compile template in functional style.

    Example:
        >>> # compile_template("template.md", {"X": 1}, "report.md")
        >>> True
        True
    """

    t = Template(template_path=template_path, assets_dir=assets_dir)
    for name, value in context.items():
        t.data([name, value])
    return t.compile(output_path=output_path)

