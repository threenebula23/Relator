"""Публичный API пакета reporting.

Этот файл нужен для локального импорта из соседних скриптов:

    from reporting import Template
"""

from .src.reporting import Template, TemplateError, compile_template

__all__ = ["Template", "TemplateError", "compile_template"]
