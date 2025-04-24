'''
# AI-Based Task Manager

Інтелектуальна десктопна програма для керування завданнями з використанням моделі T5 (Hugging Face) для генерації рекомендацій щодо виконання задач.

## 🧠 Основні можливості

- Додавання, редагування та видалення завдань
- Пріоритети та дедлайни
- Позначення завдань як виконаних
- Генерація AI-рекомендацій (T5 model, Hugging Face API)
- Локальне збереження у SQLite
- Інтуїтивний інтерфейс (Tkinter)

## 🔧 Інструкція для розробника

### Крок 1: Клонування репозиторію
```bash
git clone https://github.com/Tsuchi01/Intelligent-task-management-system.git
cd Intelligent-task-management-system
```
### Крок 2: Встановлення Python
Завантажити Python ≥3.10 з https://www.python.org
Увімкніть прапорець Add to PATH
Обов’язково додати до PATH

### Крок 3: Створити віртуальне середовище
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS
```
### Крок 4: Встановити залежності
```bash
pip install -r requirements.txt
```
Якщо немає requirements.txt, створіть вручну:
```
pip install tkinter requests pylint
pip freeze > requirements.txt
```
###  5. Отримання токена Hugging Face
Перейдіть на: https://huggingface.co/settings/tokens

Створіть персональний токен

Збережіть у файл apikey.txt або змініть ім’я в коді

### Крок 6: Запустити програму
```
python main.py
```

## 🔐 Безпека

Не додавайте token.txt до публічного репозиторію.

Файл .gitignore повинен включати його, щоб уникнути витоку токена.
```bash
apikey.txt
*.db
__pycache__/
```


## 📜 Ліцензія

Цей проєкт поширюється за умовами ліцензії MIT.

''''