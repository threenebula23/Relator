# Примеры вывода (как рендерится Markdown)

Здесь собраны **готовые фрагменты Markdown**, которые получаются после подстановки данных. Полный «все в одном» пример — [../prototyping/example/00_showcase/README.md](../prototyping/example/00_showcase/README.md).

---

## Скаляр и вложенные ключи

**Шаблон:** `Проект **[[title]]**`

**Контекст:** `title` → `"alpha"`

**Вывод:**

```markdown
Проект **alpha**
```

---

## Таблица `[[TABLE.rows]]`

**Контекст:** `rows` → `[{"USER": "Ann", "SCORE": 10}, {"USER": "Bob", "SCORE": 20}]`

**Вывод:**

```markdown
|USER|SCORE|
|---|---|
|Ann|10|
|Bob|20|
```

---

## Таблица с колонкой `#` — `[[TABLE.rows.NUMBERED]]`

**Вывод:**

```markdown
|#|USER|SCORE|
|---|---|---|
|1|Ann|10|
|2|Bob|20|
```

---

## Маркированный список `[[LIST.names]]`

**Контекст:** `names` → `["Ann", "Bob", "Chris"]`

**Вывод:**

```markdown
- Ann
- Bob
- Chris
```

---

## Нумерованный список `[[ENUM.names]]`

**Вывод:**

```markdown
1. Ann
2. Bob
3. Chris
```

---

## Цикл `%%len=VAR%%` с табличной строкой

**Шаблон (фрагмент):**

```text
%%len=NAME
|[[NAME.KEYS]]|
|[[NAME.DIVIDER]]|
|[[NAME.VALUES]]|
- [[ITEM]] ([[CELL.ONE]] / [[CELL.COUNT]])
%%
```

**Контекст:** `NAME` → `[{"USER": "Ann", "SCORE": 10}, {"USER": "Bob", "SCORE": 20}]`

**Вывод (две итерации подряд):**

```markdown
|USER|SCORE|
|---|---|
|Ann|10|
- USER: Ann, SCORE: 10 (1 / 2)
|USER|SCORE|
|---|---|
|Bob|20|
- USER: Bob, SCORE: 20 (2 / 2)
```

(Формат `[[ITEM]]` для строки-словаря — краткое перечисление полей через `format_scalar`.)

---

## Слот `@@note@@`

**Шаблон:** `Готово. @@note@@`

**После фазы `[[...]]`:** слот подставляет **сырую строку** (часто Markdown от агента).

**Вывод:**

```markdown
Готово. _Проверено в CI job #482._
```

Внутри слота символы `[[...]]` **не** обрабатываются как плейсхолдеры.

---

## Медиа `[[MEDIA.logo]]` (PIL)

**Контекст:** `Image.new("RGB", (120, 40), ...)`

**Вывод:** ссылка на сохранённый файл в `assets_dir` и стандартный Markdown-image, например:

```markdown
![logo](assets/img_<хеш>.png)
```

---

## Связь с примерами в репозитории

| Пример | Где смотреть результат |
|--------|-------------------------|
| 00_showcase | [00_showcase/README.md](../prototyping/example/00_showcase/README.md) — в README встроен пример полного вывода; запустите `build_report.py` для `dist/showcase_report.md` |
| 03_data_report | [03_data_report/README.md](../prototyping/example/03_data_report/README.md) — фрагмент вывода в README |
| 01_tests | [01_tests/README.md](../prototyping/example/01_tests/README.md) |
| 02_coverage | [02_coverage/README.md](../prototyping/example/02_coverage/README.md) |
| 04_agents | [04_agents/README.md](../prototyping/example/04_agents/README.md) |

Синтаксис шаблонов: [template-syntax.md](template-syntax.md), справочник: [placeholders.md](placeholders.md).
