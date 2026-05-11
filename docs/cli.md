# CLI

## Компиляция

```bash
relator --template template.md --context context.json --output report.md
relator --template template.md --context context.json --print
relator --template template.md --context context.json --output report.md --assets-dir ./assets
```

Нужен хотя бы один из флагов `--output` или `--print`.

`context.json` — объект JSON: ключи совпадают с именами для `template.data([name, value])`.

### Слоты в одном JSON

Ключи с префиксом `__slot__` задают слоты `@@имя@@` (значение — строка). Они **не** становятся переменными для `[[...]]`.

Пример: [../prototyping/example/context_with_slots.json](../prototyping/example/context_with_slots.json).

## Манифест шаблона

```bash
relator --template template.md --inspect
```

Печатает JSON в stdout с полями:

- `context_keys` — имена переменных корневого контекста, выведенные из плейсхолдеров и из `%%len=VAR%%`;
- `len_loop_vars` — порядок переменных циклов;
- `slot_names` — имена `@@...@@`;
- `raw_placeholders` — все токены внутри `[[...]]`;
- `placeholders_requiring_loop` — плейсхолдеры вроде `CELL.*`, `ITEM`, `*.VALUES`, которым нужен цикл.

Для проверки словаря перед рендером в Python: `validate_template_context(template, context)` из пакета `reporting`.

## Ограничения

Сложные типы (PIL, SQLAlchemy, классы Pydantic) через JSON CLI не передаются; для них используйте Python и `Template`.
