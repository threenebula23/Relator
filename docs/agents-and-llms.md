# Агенты и LLM

Как использовать relator, когда часть текста отчёта генерирует модель (CI, Cursor, внутренний бот).

## Зачем слоты `@@...@@`

- Таблицы и структурированные блоки — через `[[TABLE.var]]`, `%%len=VAR%%` и данные из JSON/Python.
- **Произвольный Markdown** от модели (списки, жирный текст, код) — через **слоты**: в шаблоне `@@summary@@`, в коде `template.slot("summary", markdown_string)` или ключ `__slot__summary` в `extra` / в `context` для `compile_template` / в JSON для CLI.

Так вы **не смешиваете** сырой текст модели с синтаксисом `[[...]]`: если модель выведет `[[foo]]`, внутри слота это останется обычным текстом, а не новым плейсхолдером.

## Антипаттерн

Вставлять ответ модели прямо в тело шаблона как «ещё один кусок markdown» с непредсказуемыми `[[` — риск сломать разбор или случайно создать плейсхолдеры. Правильно: слот или строго структурированные поля (таблица из JSON).

## Рекомендуемый pipeline

1. Описать **контракт** выхода агента (JSON Schema или Pydantic-модель).
2. Модель заполняет JSON (или вы вызываете tool с фиксированной схемой).
3. Скрипт валидирует JSON, маппит поля в `Template.data` и `Template.slot`.
4. `compile` → артефакт для людей или CI.

Пример в репозитории: [../prototyping/example/04_agents/](../prototyping/example/04_agents/) — `build_report.py`, `agent_output.json`, `template.md`.

Схема для `agent_output.json`: [../prototyping/example/04_agents/agent_output.schema.json](../prototyping/example/04_agents/agent_output.schema.json).

## Подсказка модели из шаблона отчёта

В сам шаблон можно вставить `[[PYDANTIC.MyModel.JSON_SCHEMA]]` или `[[PYDANTIC.MyModel.TABLE]]` (при установленном `relator[pydantic]`), чтобы в сгенерированном отчёте рядом с выводом была **напоминалка о форме данных** для следующей итерации или для человека.

## Манифест шаблона и `relator inspect`

Чтобы модель знала, **какие имена переменных и слоты** ожидаются, используйте:

```bash
relator inspect --template path/to/template.md
```

В stdout — JSON с полями вроде `context_keys`, `len_loop_vars`, `slot_names`, `raw_placeholders`. Удобно вставлять в системный промпт или прогонять в CI.

См. [cli.md](cli.md).

## Связанные страницы

- [Поток данных](data-flow.md)
- [Примеры вывода (рендер)](rendering-samples.md)
- [Примеры](examples.md)
- [Ошибки](errors.md)
