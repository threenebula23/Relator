# Примеры в репозитории

Каталог [../prototyping/example/](../prototyping/example/) содержит сценарии от «всё в одном» до узких кейсов.

| Папка | Описание |
|-------|----------|
| [00_showcase](../prototyping/example/00_showcase/) | **Витрина:** таблицы, списки, цикл, слот, медиа в одном отчёте; сравните `template.md` с `dist/showcase_report.md` после запуска |
| [01_tests](../prototyping/example/01_tests/) | Отчёт по результатам pytest (JSON) |
| [02_coverage](../prototyping/example/02_coverage/) | Сводка по `coverage.json` |
| [03_data_report](../prototyping/example/03_data_report/) | Отчёт по JSON/табличным данным |
| [04_agents](../prototyping/example/04_agents/) | Вставка выводов агента через слоты; схема JSON: [agent_output.schema.json](../prototyping/example/04_agents/agent_output.schema.json) |

**Как выглядит вывод** по типам плейсхолдеров (таблицы, списки, циклы, слоты) — отдельная страница [rendering-samples.md](rendering-samples.md).

Дополнительно: пример `context.json` с ключами `__slot__*` — [context_with_slots.json](../prototyping/example/context_with_slots.json) (см. [cli.md](cli.md)).

В каждой папке примера есть `README.md` с пояснением и **фрагментом готового вывода** после генерации.
