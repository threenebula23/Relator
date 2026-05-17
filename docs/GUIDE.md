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
4. `render()`, `print()` или `compile(path, save_context=...)` формируют результат; при необходимости `inject(путь_к_отчёту_или_json)` подгружает сохранённый контекст.

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
| `[[TREE.var]]` | ASCII-дерево каталогов из вложенного `dict`: ключ — имя файла или папки; **непустой** вложенный `dict` — папка с детьми; `None` или пустой `{}` — файл без потомков. Один корневой ключ даёт строку `имя/` и детей внутри; несколько ключей на верхнем уровне — корень `./`. Суффиксы: `COMPACT` (без декоративной строки `│` после корня), `DIRS_FIRST` (сначала подкаталоги, затем файлы, внутри групп по имени) |
| `[[JSON.var]]` | Значение в JSON в блоке кода Markdown. Суффиксы: `RAW` (только текст JSON без ограждения), `INLINE` (одна строка, без отступов) |
| `[[CELL.INDEX]]`, `[[CELL.ONE]]`, `[[CELL.COUNT]]` | Только внутри цикла `%%len=%%` |
| `[[ITEM]]` | Текущий элемент цикла как краткая строка |

Двухсегментные пути вида `[[seq.KEYS]]`, `[[seq.DIVIDER]]`, `[[seq.VALUES]]` относятся к **той же** переменной `seq`, что и цикл `%%len=seq%%`: `VALUES` подставляет строку таблицы для текущей итерации.

## Циклы

Открытие: строка с `%%len=ИМЯ`. Закрытие: строка с `%%`. Тело повторяется для каждого элемента последовательности `ИМЯ` из корневого контекста.

## Секция `%%render%%`

Открытие: строка ровно `%%render%%`. Закрытие: строка с `%%`. Тело обрабатывается **один раз** (плейсхолдеры, вложенные `%%len=%%` и другие `%%render%%` внутри — как в обычном шаблоне). Если в файле и цикл, и `%%render%%`, сначала обрабатывается тот блок, чья открывающая строка встречается раньше.

## Сохранение контекста и `inject`

- `compile(path, save_context=True)` — рядом с `path` создаётся JSON `stem.relator-context.json` (для `out/report.md` это `out/report.relator-context.json`) с копией контекста, пригодной для `json`: скаляры, списки и словари; объекты вроде PIL/matplotlib в JSON не попадают — вместо них строка-заглушка `<non-serializable:ИмяТипа>`. Чтобы снова вставить графики, после `inject` передайте медиа через `data`/`render(extra=...)`.
- `compile(path, save_context=Path(".../ctx.json"))` — записать контекст в указанный файл.
- `inject(путь)` — если передан `.json`, читается он; если путь к `.md`/`.html`, читается соседний `stem.relator-context.json` (или явный второй аргумент `context_path=...`). Загруженные ключи **сливаются** в текущий контекст (`update`); при `replace=True` контекст перед слиянием очищается. Дальше можно снова вызывать `data([...])` и пересобирать отчёт.

## Слоты

В шаблоне: `@@имя@@`. В коде: `template.slot("имя", "...")` или при `compile_template` / `render(extra=...)` ключи `__slot__имя` в словаре.

## Функции без класса

- `compile_template(template_path, context_dict, output_path, ..., save_context=...)` — контекст одним словарём; слоты через `__slot__*`.
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

## Пример: TREE, JSON, `%%render%%`, контекст и `inject`

Шаблон `report.md`:

```markdown
# [[title]]

[[TREE.fs]]

%%render%%
[[JSON.cfg]]
[[LIST.tags]]
%%
```

Шаблон `followup.md` (второй прогон после `inject`):

```markdown
Сводка: **[[title]]** / **[[version]]**
```

Код:

```python
from pathlib import Path
from relator import Template

assets = Path("assets")
t = Template(Path("report.md"), assets_dir=assets)
t.data(["title", "Мой отчёт"])
t.data(["version", "1.0"])
t.data(["fs", {"app": {"main.py": None}, "README.md": None}])
t.data(["cfg", {"env": "prod"}])
t.data(["tags", ["api", "docs"]])

out = Path("dist/report.md")
t.compile(out, save_context=True)
# рядом: dist/report.relator-context.json

t2 = Template(Path("followup.md"), assets_dir=assets)
t2.inject(out)
t2.compile(Path("dist/followup.md"))
```

Для графиков после `inject` снова передайте объекты в `data([...])` или пути к файлам в `assets` — в JSON они не сохраняются.

## Большой сквозной пример

Каталог [prototyping/example/99_full_reference](../prototyping/example/99_full_reference): длинный шаблон `template.md`, скрипт `build_report.py`, сгенерированный `dist/full_reference.md`.

## Ошибки

Исключение `relator.errors.TemplateError` — нехватает ключа, неверный тип для таблицы/цикла, незаполненный слот и т.д.
