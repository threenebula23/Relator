# Быстрый старт

## Установка

Из каталога пакета:

```bash
cd reporting
python -m pip install -e .
```

С тестами и интеграциями для разработки:

```bash
python -m pip install -e ".[dev]"
```

Только интеграции (Pydantic + SQLAlchemy):

```bash
python -m pip install "relator[integrations]"
```

## Минимальный пример

```python
from pathlib import Path
from reporting import Template

t = Template(Path("template.md"), assets_dir=Path("assets"))
t.data(["title", "Demo"])
t.data(["rows", [{"a": 1}, {"a": 2}]])
t.slot("footer", "_Сгенерировано relator._")
t.compile(Path("out/report.md"))
```

Шаблон `template.md`:

```markdown
# [[title]]

[[TABLE.rows]]

@@footer@@
```

## Дальше

- [Концепции](concepts.md) и [поток данных](data-flow.md)
- [Примеры вывода (рендер)](rendering-samples.md)
- [Синтаксис шаблонов](template-syntax.md)
- [Справочник плейсхолдеров](placeholders.md)
