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

## 🚀 Запуск проєкту
### 1. Клонування
git clone https://github.com/Tsuchi01/Intelligent-task-management-system.git
cd Intelligent-task-management-system

### 2. Віртуальне середовище

python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

### 3. Встановлення залежностей

pip install -r requirements.txt

### 4. Створення токена Hugging Face

Перейдіть на https://huggingface.co/settings/tokens
Створіть персональний токен
Збережіть токен у файл token.txt (або іншу назву — вкажіть у коді)

### 5. Запуск

python main.py

## 🔐 Безпека

Не додавайте token.txt до публічного репозиторію.
Файл .gitignore повинен включати його, щоб уникнути витоку токена.

## 📜 Ліцензія

Цей проєкт поширюється за умовами ліцензії MIT.

''''