# relator

`relator` — библиотека шаблонов для автогенерации отчётов в Markdown и HTML.

Главная идея:

1. Вы задаёте шаблон.
2. По шагам добавляете данные через `template.data([name, value])`.
3. Смотрите предпросмотр `template.print()`.
4. Компилируете отчёт в файл `template.compile(...)`.

**Полная документация** (установка, все плейсхолдеры, интеграции, примеры): каталог [docs/](docs/).

См. также: [поток данных](docs/data-flow.md), [концепции](docs/concepts.md), [примеры вывода Markdown](docs/rendering-samples.md), [справочник с примерами результата](docs/placeholders.md), [витрина в `prototyping/example/00_showcase`](prototyping/example/00_showcase/README.md), [агенты и LLM](docs/agents-and-llms.md), [обзор для промпта](docs/llm-overview.md), [cookbook](docs/cookbook.md).

---

## Содержание

1. [Установка](#установка)
2. [Быстрый старт](#быстрый-старт)
3. [Концепция шаблона](#концепция-шаблона)
4. [Служебные плейсхолдеры](#служебные-плейсхолдеры)
5. [Пошаговый API](#пошаговый-api)
6. [Подробные примеры](#подробные-примеры)
7. [Тяжёлые сценарии](#тяжёлые-сценарии)
8. [Media: PIL и matplotlib](#media-pil-и-matplotlib)
9. [CLI](#cli)
10. [Ошибки и отладка](#ошибки-и-отладка)
11. [FAQ](#faq)
12. [Рекомендации по архитектуре](#рекомендации-по-архитектуре)
13. [Кроссплатформенность](#кроссплатформенность)
14. [Публикация и релиз](#публикация-и-релиз)

---

## Установка

### Через pip из локального проекта

```bash
cd reporting
python -m pip install -e .
```

### Через uv из локального проекта

```bash
cd reporting
uv pip install -e .
```

### Через pip из PyPI

```bash
python -m pip install relator
```

### Через uv из PyPI

```bash
uv pip install relator
```

<<<<<<< HEAD
### Дополнительно: Pydantic и SQLAlchemy

```bash
python -m pip install "relator[pydantic]" "relator[sqlalchemy]"
# или одной группой:
python -m pip install "relator[integrations]"
```

=======
>>>>>>> 5652b1605af4b58c522420e60575abe2ce433bc2
---

## Быстрый старт

```python
from reporting import Template

template = Template("template.md")
template.data(["name", [{"USER": "Ann", "SCORE": 10}, {"USER": "Bob", "SCORE": 20}]])
template.data(["names", ["Ann", "Bob", "Chris"]])
template.print()
template.compile("report.md")
```

---

## Концепция шаблона

Шаблон — это обычный `.md` или `.html` файл.

Внутри него используются:

- блоки повторения `%%len=VAR ... %%`
- плейсхолдеры `[[...]]`

Пример:

```text
%%len=name
Строка [[CELL.ONE]] из [[CELL.COUNT]]
|[[name.KEYS]]|
|[[name.DIVIDER]]|
|[[name.VALUES]]|
%%
```

---

## Служебные плейсхолдеры

Важно: **служебные названия всегда в верхнем регистре**.

### CELL

- `[[CELL.INDEX]]` — индекс 0..N-1
- `[[CELL.ONE]]` — индекс 1..N
- `[[CELL.COUNT]]` — длина текущего цикла

### ITEM

- `[[ITEM]]` — текущий элемент в теле `%%len=VAR%%`

### TABLE

- `[[TABLE.VAR]]` — таблица
- `[[TABLE.VAR.NUMBERED]]` — таблица с колонкой `#`
- `[[TABLE.VAR.INDEX0]]` — таблица с колонкой index0

### LIST / ENUM

- `[[LIST.VAR]]` — маркированный список
- `[[ENUM.VAR]]` — нумерованный список

### MEDIA

- `[[MEDIA.VAR]]` — универсальная вставка по типу шаблона
- `[[MEDIA.VAR.PATH]]` — путь до файла
- `[[MEDIA.VAR.MD]]` — принудительный Markdown
- `[[MEDIA.VAR.HTML]]` — принудительный HTML

### Совместимость

- `[[VAR.TABLE]]`
- `[[VAR.TABLE.NUMBERED]]`

### Слоты `@@имя@@`

Именованные вставки заполняются **после** подстановки `[[...]]` и циклов `%%len%%` (сырой текст/Markdown/HTML).

- В шаблоне: `@@title_suffix@@`
- В коде: `template.slot("title_suffix", " — v2")` или `render(extra={"__slot__title_suffix": " — v2"})`

### PYDANTIC / SCHEMA

Нужен пакет: `pip install relator[pydantic]`. В контексте — подкласс `BaseModel`, инстанс или `TypeAdapter`.

- `[[PYDANTIC.VAR]]` — краткое описание и таблица полей
- `[[PYDANTIC.VAR.TABLE]]` — только таблица полей
- `[[PYDANTIC.VAR.JSON_SCHEMA]]` — JSON Schema в блоке кода
- `[[PYDANTIC.VAR.EXAMPLE]]` — пример JSON-объекта по полям JSON Schema (эвристика / `examples` в полях)
- `[[SCHEMA.VAR]]` — синоним `PYDANTIC`

### SQL / ORM

- `[[SQL.VAR]]` — значение `str` или SQLAlchemy `Executable`; вывод в fenced `sql`. Для компиляции выражений: `pip install relator[sqlalchemy]` и `Template(..., sql_dialect="sqlite")` (также `postgresql`, `mysql`).
- `[[ORM.VAR.TABLE]]` (или `.COLUMNS`) — таблица колонок для `sqlalchemy.Table` или mapped-класса с `__table__`
- `[[ORM.VAR.NAME]]` — имя таблицы
- `[[ORM.VAR.DDL]]` — `CREATE TABLE` в fenced `sql` (диалект из `sql_dialect`)

### Доступ к данным из Python (не для шаблона)

- `template.get("name")` / `get("name", default)`
- `template.table_keys("rows")` — порядок колонок как у `[[TABLE.rows]]`
- `template.pick("rows", 0, "USER")` — ячейка строки

---

## Пошаговый API

### 1) Создать объект

```python
from reporting import Template

template = Template("template.md", sql_dialect="sqlite")  # sql_dialect опционален
template.slot("intro", "_Черновик._")
```

### 2) Добавить данные по одной переменной

```python
template.data(["name", [{"USER": "Ann", "SCORE": 10}]])
template.data(["names", ["Ann", "Bob"]])
```

### 3) Посмотреть результат в консоли

```python
template.print(width=100)
```

### 4) Скомпилировать в файл

```python
template.compile("report.md")
```

### Функциональный шорткат

```python
from reporting import compile_template

compile_template(
    template_path="template.md",
    context={"name": [{"A": 1}], "names": ["x", "y"], "__slot__intro": "…"},
    output_path="report.md",
)
```

Ключи `__slot__*` в `context` задают слоты `@@intro@@` и не используются как переменные для `[[...]]`.

---

## Подробные примеры

### Пример A: таблица внутри цикла

Шаблон:

```text
%%len=rows
|[[rows.KEYS]]|
|[[rows.DIVIDER]]|
|[[rows.VALUES]]|
%%
```

Данные:

```python
rows = [
    {"CITY": "Paris", "POP": 2148},
    {"CITY": "Berlin", "POP": 3769},
]
```

### Пример B: таблица целиком

Шаблон:

```text
[[TABLE.rows]]
[[TABLE.rows.NUMBERED]]
```

### Пример C: списки

Шаблон:

```text
[[LIST.names]]
[[ENUM.names]]
```

Данные:

```python
names = ["Ann", "Bob", "Chris", "Dina"]
```

### Пример D: вложенный список

Шаблон:

```text
%%len=names
1. [[ITEM]]
   - index: [[CELL.INDEX]]
   - one: [[CELL.ONE]]
%%
```

---

## Тяжёлые сценарии

Ниже сценарии ближе к реальному продакшену.

### Сценарий 1: еженедельный отчёт команды

Цель:

- по командам показать KPI
- дать агрегированную таблицу
- вставить график

Шаблон `weekly.md`:

```text
# Еженедельный отчёт

## Команды

%%len=teams
### Команда [[ITEM]]
Индекс: [[CELL.ONE]] / [[CELL.COUNT]]
%%

## KPI
[[TABLE.kpi.NUMBERED]]

## График
[[MEDIA.kpi_chart]]
```

Код:

```python
from reporting import Template
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(6, 3))
ax = fig.add_subplot(111)
ax.plot([1, 2, 3, 4], [95, 97, 96, 99], marker="o")
ax.set_title("KPI динамика")

template = Template("weekly.md", assets_dir="weekly_assets")
template.data(["teams", ["Backend", "Frontend", "QA"]])
template.data(["kpi", [
    {"METRIC": "Coverage", "VALUE": "82%"},
    {"METRIC": "Incidents", "VALUE": "2"},
    {"METRIC": "Deploys", "VALUE": "14"},
]])
template.data(["kpi_chart", fig])
template.print()
template.compile("weekly_report.md")
```

### Сценарий 2: HTML-отчёт для менеджмента

Шаблон `management.html`:

```html
<h1>Отчёт менеджмента</h1>
<h2>Сводная таблица</h2>
[[TABLE.metrics.HTML]]
<h2>Визуализация</h2>
[[MEDIA.chart]]
```

Код:

```python
from reporting import Template
from PIL import Image

logo = Image.new("RGB", (160, 60), "navy")

template = Template("management.html", assets_dir="html_assets")
template.data(["metrics", [
    {"NAME": "Revenue", "VALUE": "1.2M"},
    {"NAME": "Cost", "VALUE": "0.7M"},
]])
template.data(["chart", logo])
template.compile("management_report.html")
```

### Сценарий 3: много отчётов в цикле по проектам

```python
from pathlib import Path
from reporting import Template

projects = {
    "alpha": {"issues": 14, "coverage": "79%"},
    "beta": {"issues": 4, "coverage": "88%"},
    "gamma": {"issues": 0, "coverage": "93%"},
}

for project_name, data in projects.items():
    t = Template("project_template.md", assets_dir=Path("assets") / project_name)
    t.data(["project_name", project_name])
    t.data(["metrics", [{"KEY": "issues", "VALUE": data["issues"]}, {"KEY": "coverage", "VALUE": data["coverage"]}]])
    t.compile(Path("reports") / f"{project_name}.md")
```

### Сценарий 4: пакетная генерация + предпросмотр только при ошибках

```python
from reporting import Template, TemplateError

def render_safe(template_path: str, out_path: str, context: dict):
    t = Template(template_path)
    for k, v in context.items():
        t.data([k, v])
    try:
        t.compile(out_path)
    except TemplateError:
        t.print()
        raise
```

---

## Media: PIL и matplotlib

### PIL.Image

```python
from PIL import Image
from reporting import Template

img = Image.new("RGB", (120, 40), "steelblue")
t = Template("template.md", assets_dir="assets")
t.data(["logo", img])
t.compile("report.md")
```

### matplotlib.figure.Figure

```python
import matplotlib.pyplot as plt
from reporting import Template

fig = plt.figure()
ax = fig.add_subplot(111)
ax.bar(["A", "B", "C"], [3, 7, 5])

t = Template("template.md")
t.data(["chart", fig])
t.compile("report.md")
```

### Управление вставкой

```text
[[MEDIA.chart]]       # авто (md/html)
[[MEDIA.chart.PATH]]  # только путь
[[MEDIA.chart.MD]]    # строго markdown
[[MEDIA.chart.HTML]]  # строго html
```

---

## CLI

### Манифест шаблона (JSON)

```bash
relator --template template.md --inspect
```

Вывод — список ожидаемых ключей контекста, слотов `@@...@@` и сырых плейсхолдеров (удобно для промпта агента и CI).

### Компиляция в файл

```bash
relator --template template.md --context context.json --output report.md
```

### Только печать

```bash
relator --template template.md --context context.json --print
```

### Пример context.json со слотами

Ключи `__slot__имя` задают слоты `@@имя@@` (не попадают в контекст `[[...]]`):

```json
{
  "rows": [{"A": 1}],
  "__slot__note": "_Черновик._"
}
```

### Пример context.json (только данные)

```json
{
  "name": [
    {"USER": "Ann", "SCORE": 10},
    {"USER": "Bob", "SCORE": 20}
  ],
  "names": ["Ann", "Bob", "Chris"]
}
```

---

### `TemplateError: Unknown placeholder root ...`

Причина:

- в шаблоне используется переменная, которую не добавили через `data`.

Решение:

- проверить имя переменной и регистр.

### `CELL.* is available only inside %%len=VAR%%`

Причина:

- `CELL` использован вне цикла.

Решение:

- перенести плейсхолдер в тело `%%len=...%%`.

### `VAR.VALUES requires %%len=VAR%% context`

Причина:

- `[[VAR.VALUES]]` использован вне своего цикла.

Решение:

- использовать `[[TABLE.VAR]]` или обернуть в `%%len=VAR%%`.

---

## FAQ

### Можно ли использовать lowercase имена переменных?

Да. Например `name`, `rows`, `items`.

### Почему служебные плейсхолдеры uppercase?

Чтобы отделять пользовательские данные от системных токенов.

### Можно ли использовать библиотеку без Rich?

Да, но метод `print()` требует `rich`.

### Можно ли рендерить только в строку без файла?

Да, через `template.render()`.

### Поддерживается ли Windows?

Да, библиотека использует `pathlib` и UTF-8.

---

## Рекомендации по архитектуре

1. Храните шаблоны в `templates/`.
2. Храните generated отчёты в `reports/`.
3. Для медиа используйте отдельную папку `assets/`.
4. Не смешивайте бизнес-логику и шаблонную логику.
5. Добавьте golden-тесты для ключевых шаблонов.

Пример структуры:

```text
project/
  templates/
    weekly.md
    management.html
  reports/
  assets/
  scripts/
    build_reports.py
```

---

## Кроссплатформенность

- операции с путями через `pathlib.Path`
- чтение/запись через UTF-8
- CI-матрица: Linux, macOS, Windows
- тестовая матрица Python: 3.9–3.13
