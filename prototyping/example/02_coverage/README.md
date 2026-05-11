# Пример: отчёт по покрытию (coverage.json)

## Как это работает

1. Запускаете тесты с `coverage run` и `coverage json -o coverage.json` (или копируете демо `sample_coverage.json`).
2. `build_report.py` агрегирует метрики в таблицу для `[[TABLE.metrics]]`.
3. При желании добавьте график: сохраните matplotlib figure в переменную и передайте в `[[MEDIA.chart]]` (см. основной README).

Запуск:

```bash
python build_report.py
```

Результат: `dist/coverage_report.md`.

## Пример вывода

```markdown
# Покрытие кода

## Общие метрики

|metric|value|
|---|---|
|percent_covered|80.0|
|covered_lines|120|
|num_statements|150|

## По файлам (ниже порога)

|file|percent_covered|
|---|---|
|src/module_b.py|62.5|
```

## Почему это удобно

- Единый Markdown для PR и внутренней wiki.
- Не нужно вручную переносить проценты из терминала.

## Экономия времени

Ручная сводка «что упало по покрытию» по файлам — **10–20 минут** на релиз; после настройки скрипта — **секунды** на генерацию файла в CI.
