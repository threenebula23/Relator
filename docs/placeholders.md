# Справочник плейсхолдеров

Служебные имена в пространствах ниже обычно в **ВЕРХНЕМ РЕГИСТРЕ**.

## CELL

Только внутри `%%len=VAR%%`.

| Плейсхолдер | Значение |
|-------------|----------|
| `[[CELL.INDEX]]` | 0 … N−1 |
| `[[CELL.ONE]]` | 1 … N |
| `[[CELL.COUNT]]` | N |

## ITEM

| Плейсхолдер | Значение |
|-------------|----------|
| `[[ITEM]]` | Текущий элемент цикла |

## TABLE

| Плейсхолдер | Значение |
|-------------|----------|
| `[[TABLE.VAR]]` | Markdown-таблица |
| `[[TABLE.VAR.NUMBERED]]` | С колонкой `#` |
| `[[TABLE.VAR.INDEX0]]` | С колонкой index0 |
| `[[TABLE.VAR.HTML]]` | HTML-таблица |

Совместимость: `[[VAR.TABLE]]`, `[[VAR.TABLE.NUMBERED]]`.

## LIST / ENUM

| Плейсхолдер | Значение |
|-------------|----------|
| `[[LIST.VAR]]` | Маркированный список |
| `[[ENUM.VAR]]` | Нумерованный список |

## MEDIA

| Плейсхолдер | Значение |
|-------------|----------|
| `[[MEDIA.VAR]]` | Авто (md/html) |
| `[[MEDIA.VAR.PATH]]` | Путь к файлу |
| `[[MEDIA.VAR.MD]]` / `[[MEDIA.VAR.HTML]]` | Принудительный формат |

## PYDANTIC / SCHEMA

Требуется `pip install relator[pydantic]`. `VAR` — имя переменной в контексте (класс `BaseModel`, инстанс или `TypeAdapter`).

| Плейсхолдер | Значение |
|-------------|----------|
| `[[PYDANTIC.VAR]]` | Кратко + таблица полей из JSON Schema |
| `[[PYDANTIC.VAR.TABLE]]` | Таблица полей |
| `[[PYDANTIC.VAR.JSON_SCHEMA]]` | JSON Schema в блоке кода |
| `[[PYDANTIC.VAR.EXAMPLE]]` | Пример объекта в fenced `json` (по JSON Schema, поля с `examples` / эвристика по `type`) |
| `[[SCHEMA.VAR...]]` | Синоним `PYDANTIC` |

## SQL

| Плейсхолдер | Значение |
|-------------|----------|
| `[[SQL.VAR]]` | Строка SQL или SQLAlchemy `Executable` в fenced `sql` |

Для компиляции выражений SQLAlchemy нужен пакет `sqlalchemy` и при необходимости `Template(..., sql_dialect="sqlite"|"postgresql"|"mysql")`.

## ORM

Требуется `sqlalchemy`. Значение — `Table` или mapped-класс с `__table__`.

| Плейсхолдер | Значение |
|-------------|----------|
| `[[ORM.VAR.TABLE]]` / `[[ORM.VAR.COLUMNS]]` | Таблица колонок |
| `[[ORM.VAR.NAME]]` | Имя таблицы |
| `[[ORM.VAR.DDL]]` | `CREATE TABLE` (диалект из `sql_dialect`) |

## Слоты (не `[[...]]`)

Синтаксис: `@@slot_name@@`. Заполняются из Python, см. [python-api.md](python-api.md).
