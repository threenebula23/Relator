# Changelog

## 1.3.0

- Плейсхолдер **`[[TREE.var]]`**: ASCII-дерево из вложенного `dict` (каталог = непустой вложенный mapping, лист = `None` или `{}`); суффиксы **`COMPACT`**, **`DIRS_FIRST`**; защита от циклов и лимит глубины.
- Плейсхолдер **`[[JSON.var]]`**: вывод значения в JSON; суффиксы **`RAW`** (без ограждения), **`INLINE`** (одна строка); по умолчанию блок кода Markdown `` ```json ``.
- Блок **`%%render%%`** … **`%%`**: тело шаблона рендерится один раз; вместе с **`%%len=%%`** выбирается блок с меньшим номером строки открытия.
- **`Template.compile(..., save_context=True | Path)`**: сохранение контекста в JSON (`stem.relator-context.json` рядом с отчётом или явный путь); несериализуемые значения заменяются на строку `<non-serializable:ИмяТипа>`.
- **`Template.inject(source, *, context_path=..., replace=False)`**: загрузка контекста из `.json` или соседнего `*.relator-context.json` для `.md`/`.html`; слияние в `_data`, опционально полная замена контекста.
- **`compile_template(..., save_context=...)`**: проброс сохранения контекста.
- Манифест шаблона учитывает ключи **`TREE`** и **`JSON`**; обновлён [docs/GUIDE.md](docs/GUIDE.md).

## 1.2.0

- **Breaking:** пакет для импорта переименован с `reporting` на `relator` (`from relator import Template`). CLI по-прежнему команда `relator`.
- Документация сведена в [docs/GUIDE.md](docs/GUIDE.md); добавлен пример [prototyping/example/99_full_reference/](prototyping/example/99_full_reference/).

## 1.1

- Added named slots `@@slot_name@@` filled after placeholder rendering; `Template.slot(name, value)` and `extra` keys `__slot__name`.
- Added Python-only context helpers on `Template`: `get()`, `table_keys()`, `pick()` (for building pipelines without touching `_data` directly).
- Added `[[PYDANTIC.VAR]]` / `[[SCHEMA.VAR]]` with modes `.TABLE`, `.JSON_SCHEMA`, `.EXAMPLE` (optional extra `relator[pydantic]`).
- Added `[[SQL.VAR]]` for fenced SQL from strings or SQLAlchemy executables; `[[ORM.VAR]]` with `.TABLE`, `.NAME`, `.DDL` (optional `relator[sqlalchemy]`).
- Added `Template(..., sql_dialect=...)` and `compile_template(..., sql_dialect=...)` for SQL/DDL compilation (`sqlite`, `postgresql`, `mysql`).
- Added documentation under `reporting/docs/` and runnable scenarios under `reporting/prototyping/example/`.
- Updated `[project.urls]` to the [Relator](https://github.com/threenebula23/Relator) GitHub repository.

## 1.0

- Introduced step-by-step `Template` API.
- Added `%%len=VAR%%` blocks and `[[...]]` placeholders.
- Added service namespaces: `CELL`, `TABLE`, `LIST`, `ENUM`, `MEDIA`, `ITEM`.
- Added Rich preview via `template.print()`.
- Added PIL/matplotlib media integration.
- Added cross-platform CI matrix and pytest tests.
