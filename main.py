import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sqlite3
import http.client
import json
import time


# Клас для інтеграції з моделью T5 через API
class T5Helper:
    def __init__(self, api_url="api-inference.huggingface.co", token_file="лол"):
        self.api_url = api_url  # URL API моделі
        self.api_token = self.load_token(token_file)  # Токен авторизації

    def load_token(self, token_file):
        try:
            with open(token_file, "r") as file:
                return file.readline().strip()
        except FileNotFoundError:
            print(f"Файл {token_file} не знайдено. Перевірте шлях.")
            return ""

    # Запит до API для отримання відповіді на промт
    def query(self, prompt):
        conn = http.client.HTTPSConnection(self.api_url)
        payload = json.dumps({"inputs": prompt})
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        try:
            conn.request("POST", "/models/t5-large", payload, headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            if res.status == 200:
                return json.loads(data)
            elif res.status == 503:
                # Якщо модель ще завантажується, чекаємо і намагаємося знову
                print("Модель ще завантажується, повторюємо запит...")
                time.sleep(10)
                return self.query(prompt)
            else:
                return {"error": data, "status_code": res.status}
        except Exception as e:
            return {"error": str(e), "status_code": 500}

    # Генерація рекомендацій для списку завдань
    def generate_suggestions(self, tasks):
        if not tasks:
            return "Немає завдань для аналізу."

        recommendations = []
        for task in tasks:
            task_id, title, description, deadline, completed, priority = task

            # Покращений промт для отримання більш детальних рекомендацій
            prompt = f"""
            Завдання: "{title}"
            Опис завдання: {description}
            Дедлайн: {deadline}
            Пріоритет: {priority} (1 - найвищий, 5 - найнижчий)

            Задача: на основі цього завдання, надайте рекомендації щодо кроків для досягнення успіху:
            1. Як організувати час для виконання цього завдання?
            2. Як можна зменшити складність завдання?
            3. Як визначити, коли завдання буде виконано вчасно?
            """

            response = self.query(prompt)

            # Перевірка на помилки у відповіді
            if "error" in response:
                recommendations.append(f"Помилка для '{title}': {response['error']}")
            else:
                print(f"Response for task '{title}': {response}")  # Виводимо всю відповідь для налагодження

                # Перевірка на наявність тексту в відповіді
                generated_text = None
                if isinstance(response, list) and len(response) > 0:
                    if 'generated_text' in response[0]:
                        generated_text = response[0]['generated_text']

                if generated_text:
                    recommendations.append(f"Завдання: {title}\nРекомендація: {generated_text}\n")
                else:
                    recommendations.append(f"Завдання: {title}\nРекомендація: (Текст не знайдений у відповіді)\n")

        return "\n".join(recommendations) if recommendations else "Не вдалося отримати рекомендації для завдань."


# Клас для управління завданнями
class TaskManager:
    def __init__(self):
        self.db_name = "tasks.db"
        self.tasks = []
        self.create_db()

    def create_db(self):
        # Створення або підключення до бази даних
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                deadline TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                priority INTEGER NOT NULL DEFAULT 3
            )
        """)
        conn.commit()
        conn.close()

    def load_tasks(self):
        # Завантаження завдань з бази даних
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, deadline, completed, priority FROM tasks")
        self.tasks = cursor.fetchall()
        conn.close()

    def add_task(self, title, description, deadline, priority):
        # Додавання нового завдання в базу
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, description, deadline, priority)
            VALUES (?, ?, ?, ?)
        """, (title, description, deadline, priority))
        conn.commit()
        conn.close()

    def mark_task_completed(self, task_id):
        # Позначення завдання як виконаного
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    def delete_task(self, task_id):
        # Видалення завдання з бази
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()


# Інтерфейс Tkinter
class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager with AI Suggestions")

        self.manager = TaskManager()
        self.t5 = T5Helper()

        # Інтерфейс
        self.title_label = tk.Label(root, text="Назва завдання")
        self.title_label.pack(padx=10, pady=5)
        self.title_entry = tk.Entry(root, width=40)
        self.title_entry.pack(padx=10, pady=5)

        self.desc_label = tk.Label(root, text="Опис завдання")
        self.desc_label.pack(padx=10, pady=5)
        self.desc_entry = tk.Entry(root, width=40)
        self.desc_entry.pack(padx=10, pady=5)

        self.deadline_label = tk.Label(root, text="Дедлайн (YYYY-MM-DD HH:MM)")
        self.deadline_label.pack(padx=10, pady=5)
        self.deadline_entry = tk.Entry(root, width=40)
        self.deadline_entry.pack(padx=10, pady=5)

        self.priority_label = tk.Label(root, text="Пріоритет (1-5)")
        self.priority_label.pack(padx=10, pady=5)
        self.priority_entry = tk.Entry(root, width=40)
        self.priority_entry.pack(padx=10, pady=5)

        # Кнопка для додавання завдання
        self.add_button = tk.Button(root, text="Додати завдання", command=self.add_task)
        self.add_button.pack(padx=10, pady=10)

        # Кнопка для отримання рекомендацій
        self.suggestions_button = tk.Button(root, text="Отримати рекомендації", command=self.get_ai_suggestions)
        self.suggestions_button.pack(padx=10, pady=10)

        # Список завдань
        self.tasks_label = tk.Label(root, text="Список завдань")
        self.tasks_label.pack(padx=10, pady=5)
        self.tasks_listbox = tk.Listbox(root, width=80, height=10)
        self.tasks_listbox.pack(padx=10, pady=10)

        # Кнопки для помітки як виконаного та видалення
        self.mark_completed_button = tk.Button(root, text="Позначити як виконане", command=self.mark_task_completed)
        self.mark_completed_button.pack(padx=10, pady=5)

        self.delete_button = tk.Button(root, text="Видалити завдання", command=self.delete_task)
        self.delete_button.pack(padx=10, pady=5)

        self.load_tasks()

    def load_tasks(self):
        self.manager.load_tasks()
        self.tasks_listbox.delete(0, tk.END)
        for task in self.manager.tasks:
            task_id, title, description, deadline, completed, priority = task
            display_text = f"{task_id}: {title} (Пріоритет: {priority}, Дедлайн: {deadline})"
            if completed == 1:
                display_text += " - Виконано"
            self.tasks_listbox.insert(tk.END, display_text)

    def add_task(self):
        title = self.title_entry.get()
        description = self.desc_entry.get()
        deadline = self.deadline_entry.get()
        try:
            priority = int(self.priority_entry.get())
            if not (1 <= priority <= 5):
                raise ValueError
        except ValueError:
            messagebox.showerror("Помилка", "Пріоритет повинен бути числом від 1 до 5.")
            return

        self.manager.add_task(title, description, deadline, priority)
        self.load_tasks()
        self.clear_entries()

    def get_ai_suggestions(self):
        suggestions = self.t5.generate_suggestions(self.manager.tasks)
        messagebox.showinfo("Рекомендації", suggestions)

    def mark_task_completed(self):
        try:
            selected_task_index = self.tasks_listbox.curselection()[0]
            selected_task = self.manager.tasks[selected_task_index]
            task_id = selected_task[0]
            self.manager.mark_task_completed(task_id)
            self.load_tasks()
        except IndexError:
            messagebox.showerror("Помилка", "Будь ласка, виберіть завдання.")

    def delete_task(self):
        try:
            selected_task_index = self.tasks_listbox.curselection()[0]
            selected_task = self.manager.tasks[selected_task_index]
            task_id = selected_task[0]
            self.manager.delete_task(task_id)
            self.load_tasks()
        except IndexError:
            messagebox.showerror("Помилка", "Будь ласка, виберіть завдання.")

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)


# Створення основного вікна
root = tk.Tk()
app = TaskApp(root)
root.mainloop()
