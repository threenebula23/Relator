# Пример: отчёт по тестам (pytest JSON)

## Как это работает

1. Генерируется или сохраняется JSON со сводкой прогона (в реальном CI — через [pytest-json-report](https://pypi.org/project/pytest-json-report/) или свой экспорт).
2. Скрипт `build_report.py` читает JSON, раскладывает данные в `Template.data()`.
3. Шаблон `template.md` выводит таблицу упавших тестов и слот `@@ci_note@@` для произвольной строки из CI.

Запуск (из этой папки, при установленном `relator`):

```bash
python build_report.py
```

Отчёт: `dist/test_report.md`.

## Пример вывода

После `python build_report.py` верх отчёта выглядит так:

```markdown
# Отчёт по тестам

_Демо: см. `README.md` в этой папке._

## Сводка

|total|passed|failed|skipped|
|---|---|---|---|
|42|40|2|0|

## Упавшие тесты

|nodeid|message|
|---|---|
|tests/test_api.py::test_create|AssertionError: status 500|
|tests/test_auth.py::test_token|Timeout|
```

## Почему это удобно

- Один шаблон для всех веток и nightly-сборок.
- Таблицы и списки в Markdown без ручной склейки строк.
- Слот `@@ci_note@@` для ссылки на лог job без правки шаблона.

## Экономия времени

Ручной разбор `pytest` лога и копирование в Confluence/PR занимает **5–15 минут** на прогон; скрипт + шаблон после настройки занимают **меньше минуты** на машине CI.
