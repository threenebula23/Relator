# Changelog

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
