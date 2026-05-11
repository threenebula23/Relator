# Справочник плейсхолдеров

Служебные имена в пространствах ниже обычно в **ВЕРХНЕМ РЕГИСТРЕ**.

Ниже в разделах после таблиц — блоки **«Результат в отчёте»**: это **буквальный** фрагмент Markdown/HTML, который попадёт в выходной файл при указанных данных (как после `compile`).

Полная подборка по сценариям: [rendering-samples.md](rendering-samples.md).

---

## CELL

Только внутри `%%len=VAR%%`.

| Плейсхолдер | Значение |
|-------------|----------|
| `[[CELL.INDEX]]` | 0 … N−1 |
| `[[CELL.ONE]]` | 1 … N |
| `[[CELL.COUNT]]` | N |

**Результат в отчёте** (вместе с циклом и `[[ITEM]]`): шаблон `%%len=x\n[[CELL.ONE]]/[[CELL.COUNT]]: [[ITEM]]\n%%`, данные `x` → `[10, 20]`:

```markdown
1/2: 10
2/2: 20
```

---

## ITEM

| Плейсхолдер | Значение |
|-------------|----------|
| `[[ITEM]]` | Текущий элемент цикла |

**Результат в отчёте:** для одной итерации с элементом-объектом `{"A": 1}` плейсхолдер `[[ITEM]]` даёт строку:

```markdown
A: 1
```

Для примитива `42` в теле цикла `[[ITEM]]` даёт:

```markdown
42
```

---

## TABLE

| Плейсхолдер | Значение |
|-------------|----------|
| `[[TABLE.VAR]]` | Markdown-таблица |
| `[[TABLE.VAR.NUMBERED]]` | С колонкой `#` |
| `[[TABLE.VAR.INDEX0]]` | С колонкой index0 |
| `[[TABLE.VAR.HTML]]` | HTML-таблица |

Совместимость: `[[VAR.TABLE]]`, `[[VAR.TABLE.NUMBERED]]`.

**Данные:** `rows` → `[{"USER": "Ann", "SCORE": 10}, {"USER": "Bob", "SCORE": 20}]`

**Результат для `[[TABLE.rows]]` в отчёте:**

```markdown
|USER|SCORE|
|---|---|
|Ann|10|
|Bob|20|
```

**Результат для `[[TABLE.rows.NUMBERED]]`:**

```markdown
|#|USER|SCORE|
|---|---|---|
|1|Ann|10|
|2|Bob|20|
```

**Результат для `[[TABLE.rows.INDEX0]]`:**

```markdown
|#|USER|SCORE|
|---|---|---|
|0|Ann|10|
|1|Bob|20|
```

(Первая колонка — индекс с нуля; заголовок колонки в разметке по-прежнему оформляется как у `INDEX0` в движке.)

**Результат для `[[TABLE.rows.HTML]]` (фрагмент):**

```html
<table><thead><tr><th>USER</th><th>SCORE</th></tr></thead><tbody><tr><td>Ann</td><td>10</td></tr><tr><td>Bob</td><td>20</td></tr></tbody></table>
```

---

## LIST / ENUM

| Плейсхолдер | Значение |
|-------------|----------|
| `[[LIST.VAR]]` | Маркированный список |
| `[[ENUM.VAR]]` | Нумерованный список |

**Данные:** `names` → `["Ann", "Bob"]`

**Результат `[[LIST.names]]` в отчёте:**

```markdown
- Ann
- Bob
```

**Результат `[[ENUM.names]]`:**

```markdown
1. Ann
2. Bob
```

---

## MEDIA

| Плейсхолдер | Значение |
|-------------|----------|
| `[[MEDIA.VAR]]` | Авто (md/html) |
| `[[MEDIA.VAR.PATH]]` | Путь к файлу |
| `[[MEDIA.VAR.MD]]` / `[[MEDIA.VAR.HTML]]` | Принудительный формат |

**Результат в отчёте (Markdown):** для PIL-картинки в `.md` шаблоне обычно получается строка вида:

```markdown
![VARNAME](assets/img_<хеш>.png)
```

Файл кладётся в `assets_dir`; имя стабильно при тех же байтах изображения.

---

## PYDANTIC / SCHEMA

Требуется `pip install relator[pydantic]`. `VAR` — имя переменной в контексте (класс `BaseModel`, инстанс или `TypeAdapter`).

| Плейсхолдер | Значение |
|-------------|----------|
| `[[PYDANTIC.VAR]]` | Кратко + таблица полей из JSON Schema |
| `[[PYDANTIC.VAR.TABLE]]` | Таблица полей |
| `[[PYDANTIC.VAR.JSON_SCHEMA]]` | JSON Schema в блоке кода |
| `[[PYDANTIC.VAR.EXAMPLE]]` | Пример объекта в fenced `json` (по JSON Schema, поля с `examples` / эвристика по `type`) |
| `[[SCHEMA.VAR...]]` | Синоним `PYDANTIC` |

**Результат `[[PYDANTIC.M.TABLE]]`** для модели с полем `a: int` (упрощённо):

```markdown
|field|type|required|default|description|
|---|---|---|---|---|
|a|integer|False|||
```

**Результат `[[PYDANTIC.M.JSON_SCHEMA]]` в отчёте** — блок кода `json` с полной JSON Schema модели (фрагмент начала):

````markdown
```json
{
  "properties": {
    "a": {
      "title": "A",
      "type": "integer"
    }
  },
  "required": [],
  "title": "M",
  "type": "object"
}
```
````

---

## SQL

| Плейсхолдер | Значение |
|-------------|----------|
| `[[SQL.VAR]]` | Строка SQL или SQLAlchemy `Executable` в fenced `sql` |

Для компиляции выражений SQLAlchemy нужен пакет `sqlalchemy` и при необходимости `Template(..., sql_dialect="sqlite"|"postgresql"|"mysql")`.

**Результат в отчёте** для `[[SQL.q]]`, если в контексте `q` → строка `"SELECT 1;"`, в Markdown-шаблоне:

````markdown
```sql
SELECT 1;
```
````

---

## ORM

Требуется `sqlalchemy`. Значение — `Table` или mapped-класс с `__table__`.

| Плейсхолдер | Значение |
|-------------|----------|
| `[[ORM.VAR.TABLE]]` / `[[ORM.VAR.COLUMNS]]` | Таблица колонок |
| `[[ORM.VAR.NAME]]` | Имя таблицы |
| `[[ORM.VAR.DDL]]` | `CREATE TABLE` (диалект из `sql_dialect`) |

**Результат `[[ORM.t.NAME]]` в отчёте** (одна строка текста):

```markdown
users
```

**Результат `[[ORM.t.TABLE]]`** — Markdown-таблица колонок (вид зависит от таблицы), например:

```markdown
|column|type|nullable|default|primary_key|
|---|---|---|---|---|
|id|INTEGER|False||True|
|name|VARCHAR(32)|True||False|
```

**Результат `[[ORM.t.DDL]]`:** один fenced-блок `sql` с `CREATE TABLE ...` для выбранного `sql_dialect`.

---

## Слоты (не `[[...]]`)

Синтаксис: `@@slot_name@@`. Заполняются из Python, см. [python-api.md](python-api.md).

**Шаблон:** `Статус: @@status@@`

**После `template.slot("status", "✅ OK")` в отчёте:**

```markdown
Статус: ✅ OK
```

Подстановка слота — **последний** шаг: в тексте слота `[[...]]` больше не обрабатываются.
