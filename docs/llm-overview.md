# Краткий обзор для LLM

Используйте как сжатый контекст для промпта (1–2 экрана).

- **Шаблон**: `.md` / `.html` с `[[...]]`, циклами `%%len=VAR%% ... %%`, слотами `@@name@@`.
- **Данные**: `Template(path).data(["varName", value])` — цепочка; затем `compile("out.md")`.
- **Слоты**: произвольный текст/Markdown — `template.slot("name", "...")` или ключи `__slot__name` в `extra` / в словаре для `compile_template` / в JSON для CLI.
- **Порядок рендера**: сначала `[[...]]` и циклы, потом `@@слоты@@` ([data-flow.md](data-flow.md)).
- **Контракт шаблона**: `relator inspect --template file.md` → JSON с `context_keys`, `slot_names`, `raw_placeholders` ([cli.md](cli.md)).
- **Примеры готового Markdown**: [rendering-samples.md](rendering-samples.md).
- **Проверка входа**: `validate_template_context(template, dict)` из пакета `reporting`.
- **Агенты**: паттерн JSON + слоты — [agents-and-llms.md](agents-and-llms.md), пример [../prototyping/example/04_agents/](../prototyping/example/04_agents/).

Полная навигация: [index.md](index.md).
