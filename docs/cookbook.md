# Cookbook

Короткие рецепты: шаблон + несколько строк Python. Как выглядит **готовый** Markdown по каждому типу — [rendering-samples.md](rendering-samples.md).

## Только таблица

Шаблон:

```markdown
[[TABLE.rows]]
```

Код:

```python
from reporting import Template

Template("tpl.md").data(["rows", [{"A": 1}, {"A": 2}]]).compile("out.md")
```

## Цикл и ячейка

Шаблон:

```markdown
%%len=items
- [[ITEM]] ([[CELL.ONE]] / [[CELL.COUNT]])
%%
```

Код:

```python
Template("tpl.md").data(["items", ["a", "b"]]).compile("out.md")
```

## Медиа (PIL)

Шаблон:

```markdown
[[MEDIA.chart]]
```

Код:

```python
from PIL import Image
from reporting import Template

img = Image.new("RGB", (40, 20), "gray")
Template("tpl.md", assets_dir="assets").data(["chart", img]).compile("out.md")
```

## HTML-таблица

Шаблон `report.html`:

```html
[[TABLE.rows.HTML]]
```

Код:

```python
Template("report.html").data(["rows", [{"X": 1}]]).compile("out.html")
```

## Агент: таблица + слоты

Шаблон:

```markdown
@@summary@@

[[TABLE.tasks]]
```

Код:

```python
from reporting import Template

t = Template("tpl.md")
t.data(["tasks", [{"id": "1", "title": "Fix"}]])
t.slot("summary", "## Итог\n\nГотово.")
t.compile("out.md")
```

Или один словарь с `compile_template` и ключами `__slot__summary` (см. [data-flow.md](data-flow.md)).

## Проверка контекста до рендера

```python
from reporting import validate_template_context

validate_template_context("tpl.md", {"rows": [], "__slot__note": "x"})
```
