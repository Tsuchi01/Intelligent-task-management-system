# Linting: Документація

# Статичний аналіз коду з Pylint

## 🔍 Обраний інструмент

**Pylint** — один з найпотужніших і найгнучкіших лінтерів для Python. Він дозволяє:
- знаходити синтаксичні та логічні помилки,
- перевіряти стиль коду за стандартом PEP8,
- виявляти потенційно небезпечні конструкції,
- контролювати складність та якість проєкту.


## ⚙️ Конфігурація (.pylintrc)

Файл `.pylintrc` було налаштовано відповідно до специфіки проєкту, що включає використання Tkinter, SQLite та API-запитів. Деякі перевірки були вимкнені свідомо, оскільки вони не є критичними у рамках цього застосунку.

```ini
[MASTER]
ignore=.venv

[MESSAGES CONTROL]
disable=
    C0114,  # missing-module-docstring
    C0115,  # missing-class-docstring
    C0116,  # missing-function-docstring
    W0612,  # unused-variable
    W0611,  # unused-import
    W0718,  # broad-exception-caught
    R0902   # too-many-instance-attributes

[FORMAT]
max-line-length=130

[DESIGN]
max-attributes=18
## Як запустити лінтер
```bash
pylint main.py