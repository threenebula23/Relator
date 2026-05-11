# Ошибки и отладка

## Матрица: сообщение → что сделать

| Сообщение / ситуация | Причина | Что сделать |
|----------------------|---------|-------------|
| `Unknown placeholder root 'X'` | Нет `data(["X", ...])` / ключа в JSON | Добавить переменную с тем же именем и регистром |
| `CELL.* is available only inside %%len=VAR%%` | `[[CELL.…]]` вне цикла | Обернуть в `%%len=…%%` или убрать `CELL` |
| `ITEM is available only inside %%len=VAR%%` | `[[ITEM]]` вне цикла | Поместить внутрь соответствующего `%%len=VAR%%` |
| `VAR.VALUES requires %%len=VAR%% context` | `[[VAR.VALUES]]` без цикла по `VAR` | Использовать `[[TABLE.VAR]]` или цикл `%%len=VAR%%` |
| `Missing slot value(s) for: …` | В шаблоне `@@name@@`, нет `slot` / `__slot__name` | Задать все слоты из манифеста (`relator inspect`) |
| `missing context keys` / `missing slots` (`validate_template_context`) | Неполный словарь до `compile` | Дополнить ключи или ослабить проверку |
| `Unknown loop variable 'VAR' in %%len=...%%` | Нет последовательности для цикла | `data(["VAR", [...]])` |
| `Loop variable 'VAR' must be sequence-like` | Передана строка или не-последовательность | Передать список / кортеж |
| Pydantic / SQL «requires pip install» | Нет optional-зависимости | `pip install relator[pydantic]` или `[sqlalchemy]` |

## `TemplateError: Unknown placeholder root`

В шаблоне используется переменная, не переданная через `data([...])`.

## `CELL.* is available only inside %%len=VAR%%`

Плейсхолдер `CELL` вне тела цикла.

## `Missing slot value(s) for: ...`

В шаблоне есть `@@name@@`, но не задано значение через `slot()` или `__slot__name` в `extra` / JSON.

## Pydantic / SQLAlchemy

Сообщения вида «requires: pip install relator[pydantic]» означают, что в шаблоне есть `[[PYDANTIC...]]` / `[[ORM...]]`, а optional-зависимость не установлена.

## Отладка

Используйте `template.print()` перед `compile()`, чтобы увидеть результат в терминале с подсветкой Markdown.

Список ожидаемых ключей: `relator --template … --inspect` или `build_template_manifest(...)`.
