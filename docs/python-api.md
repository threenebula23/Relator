# Python API

## `Template`

### Конструктор

```python
Template(template_path, assets_dir=None, sql_dialect=None)
```

- `template_path` — путь к `.md` или `.html`.
- `assets_dir` — каталог для экспорта медиа (по умолчанию `assets`).
- `sql_dialect` — диалект для `[[SQL.*]]` / `[[ORM.*.DDL]]`: `sqlite`, `postgresql`, `mysql`.

### Данные

```python
template.data(["varName", value])  # цепочка: возвращает self
```

### Слоты

```python
template.slot("intro", "Текст для @@intro@@")
```

Либо при рендере:

```python
template.render(extra={"__slot__intro": "..."})
```

Ключи `__slot__*` не попадают в контекст плейсхолдеров `[[...]]`.

### Рендер

- `render(extra=None) -> str` — строка отчёта.
- `print(extra=None, width=100) -> str` — то же + вывод в терминал (Rich).
- `compile(output_path, extra=None) -> Path` — запись в файл.

**Пример:** шаблон `# [[t]]`, данные `t` → `"Hi"` → в файле одна строка `# Hi`. Таблицы и списки см. [placeholders.md](placeholders.md) и [rendering-samples.md](rendering-samples.md).

### Доступ к контексту (без шаблона)

Удобно в скриптах сборки отчёта, тестах, CI:

```python
template.get("rows")                 # KeyError-подобно: TemplateError если нет ключа
template.get("rows", [])             # с default
template.table_keys("rows")          # порядок колонок как у TABLE
template.pick("rows", 0, "USER")     # строка 0, колонка USER
```

## `compile_template`

Функциональный стиль:

```python
from reporting import compile_template

compile_template(
    "template.md",
    {"X": 1, "__slot__intro": "…"},
    "report.md",
    assets_dir="assets",
    sql_dialect="sqlite",
    extra={"__slot__intro": "перекрывает ключ из context при совпадении"},
)
```

Ключи `__slot__*` в словаре контекста обрабатываются как слоты (как `Template.render(..., extra=…)`). Дополнительный аргумент `extra` необязателен; при совпадении ключей значения из `extra` перезаписывают значения из `context`.

## Манифест и валидация

```python
from reporting import build_template_manifest, validate_template_context

build_template_manifest("template.md")  # dict
validate_template_context("template.md", {"rows": [], "__slot__note": "x"})
```

`validate_template_context` бросает `TemplateError`, если не хватает ключа для `[[...]]` или `__slot__*` для `@@...@@`.
