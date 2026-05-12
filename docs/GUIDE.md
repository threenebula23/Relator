# Руководство по relator

Библиотека на PyPI называется **relator**, импорт в Python: `relator` (не имя пакета из каталога репозитория).

## Установка

```bash
pip install relator
pip install "relator[integrations]"
```

Разработка из клона: каталог с `pyproject.toml`, затем `pip install -e .` или `PYTHONPATH=src` при запуске скриптов.

## Схема работы

1. Файл шаблона `.md` или `.html`.
2. `Template(path, assets_dir=..., sql_dialect=...)` читает файл.
3. `data(["имя", значение])` и при необходимости `slot("имя", "текст")` задают контекст.
4. `render()`, `print()` или `compile(path)` формируют результат.

Суффикс шаблона задаёт режим медиа: для `.html` вывод картинок ближе к HTML, для `.md` — Markdown-вставки.

## Плейсхолдеры `[[...]]`

Имена служебных пространств пишутся **заглавными** (`TABLE`, `LIST`, …).

| Запись | Назначение |
|--------|------------|
| `[[имя]]` | Значение из контекста; путь `[[a.b]]` — вложенный ключ или атрибут, если первый сегмент не совпал с правилами ниже |
| `[[TABLE.var]]` | Таблица Markdown по списку словарей `var` |
| `[[TABLE.var.NUMBERED]]` | Та же таблица с колонкой `#` 1…N |
| `[[TABLE.var.INDEX0]]` | Колонка `#` с индексами 0…N-1 |
| `[[TABLE.var.HTML]]` | HTML `<table>` |
| `[[LIST.var]]` | Маркированный список |
| `[[ENUM.var]]` | Нумерованный список |
| `[[MEDIA.var]]` | Картинка (PIL, matplotlib Figure, путь к файлу); файлы пишутся в `assets_dir` |
| `[[MEDIA.var.PATH]]` | Путь к сохранённому файлу |
| `[[MEDIA.var.HTML]]` / `[[MEDIA.var.MD]]` | Явный формат вставки |
| `[[SQL.var]]` | SQL из строки или объекта с текстом запроса (см. исходники при сложных типах) |
| `[[ORM.var.TABLE]]`, `[[ORM.var.NAME]]`, `[[ORM.var.DDL]]` | Таблица SQLAlchemy; нужен `relator[sqlalchemy]`, для DDL полезен `sql_dialect` в конструкторе |
| `[[PYDANTIC.M.TABLE]]`, `[[PYDANTIC.M.JSON_SCHEMA]]`, `[[PYDANTIC.M.EXAMPLE]]` | Pydantic-модель или класс; `[[SCHEMA.M]]` — схожий вывод |
| `[[CELL.INDEX]]`, `[[CELL.ONE]]`, `[[CELL.COUNT]]` | Только внутри цикла `%%len=%%` |
| `[[ITEM]]` | Текущий элемент цикла как краткая строка |

Двухсегментные пути вида `[[seq.KEYS]]`, `[[seq.DIVIDER]]`, `[[seq.VALUES]]` относятся к **той же** переменной `seq`, что и цикл `%%len=seq%%`: `VALUES` подставляет строку таблицы для текущей итерации.

## Циклы

Открытие: строка с `%%len=ИМЯ`. Закрытие: строка с `%%`. Тело повторяется для каждого элемента последовательности `ИМЯ` из корневого контекста.

## Слоты

В шаблоне: `@@имя@@`. В коде: `template.slot("имя", "...")` или при `compile_template` / `render(extra=...)` ключи `__slot__имя` в словаре.

## Функции без класса

- `compile_template(template_path, context_dict, output_path, ...)` — контекст одним словарём; слоты через `__slot__*`.
- `build_template_manifest(template)` — какие ключи и слоты ожидаются.
- `validate_template_context(template, context)` — проверка до рендера; бросает `TemplateError`.

Низкоуровневый `relator.engine.render_template(text, root_context, assets_dir, kind, ...)` полезен для коротких строк без файла.

## CLI

```bash
relator --template path.md --inspect
relator --template path.md --context ctx.json --output out.md
```

## Пример: шаблон и код

Шаблон `hello.md`:

```markdown
# [[title]]

@@note@@

[[TABLE.rows]]

%%len=rows
- [[CELL.ONE]]: [[ITEM]]
%%
```

Код:

```python
from pathlib import Path
from relator import Template

t = Template(Path("hello.md"), assets_dir=Path("assets"))
t.data(["title", "Отчёт"])
t.data(["rows", [{"k": 1}, {"k": 2}]])
t.slot("note", "Подпись.")
t.compile(Path("out.md"))
```

У `data` один аргумент — пара `[имя, значение]`.

## Большой сквозной пример

Каталог [prototyping/example/99_full_reference](../prototyping/example/99_full_reference): длинный шаблон `template.md`, скрипт `build_report.py`, сгенерированный `dist/full_reference.md`.

## Ошибки

Исключение `relator.errors.TemplateError` — нехватает ключа, неверный тип для таблицы/цикла, незаполненный слот и т.д.
