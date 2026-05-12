# relator

Шаблоны Markdown/HTML для отчётов: таблицы, списки, циклы `%%len=%%`, слоты `@@...@@`, медиа (Pillow, matplotlib), опционально Pydantic и SQLAlchemy.

## Установка

```bash
pip install relator
pip install "relator[integrations]"
```

## Импорт

```python
from relator import Template

t = Template("template.md", assets_dir="assets")
t.data(["title", "Заголовок"])
t.compile("out.md")
```

## Документация

[docs/GUIDE.md](docs/GUIDE.md) — синтаксис, API, пример шаблон + код.

[prototyping/example/99_full_reference/](prototyping/example/99_full_reference/) — длинный шаблон и скрипт сборки.

Остальные сценарии: [prototyping/example/README.md](prototyping/example/README.md).

## CLI

```bash
relator --template template.md --inspect
relator --template template.md --context ctx.json --output report.md
```

## Релиз на PyPI

```bash
python -m build
twine check dist/*
twine upload dist/*
```

Версию меняйте в `pyproject.toml`. Токен PyPI храните только в переменных окружения или в CI, не в репозитории.
