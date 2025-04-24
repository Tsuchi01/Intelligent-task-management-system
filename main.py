"""Модуль управління завданнями з AI-рекомендаціями через Tkinter і T5."""

import sqlite3
import http.client
import json
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


class T5Helper:
    """Клас для інтеграції з моделлю T5 через API."""

    def __init__(self, api_url="api-inference.huggingface.co", token_file="apikey.txt"):
        self.api_url = api_url
        self.api_token = self.load_token(token_file)

    def load_token(self, token_file):
        """Завантажує токен з файлу."""
        try:
            with open(token_file, "r", encoding="utf-8") as file:
                return file.readline().strip()
        except FileNotFoundError:
            print(f"Файл {token_file} не знайдено. Перевірте шлях.")
            return ""

    def query(self, prompt):
        """Виконує запит до моделі T5."""
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
            if res.status == 503:
                print("Модель ще завантажується, повторюємо запит...")
                time.sleep(10)
                return self.query(prompt)
            return {"error": data, "status_code": res.status}
        except Exception as exc:
            return {"error": str(exc), "status_code": 500}

    def generate_suggestions(self, tasks):
        """Генерує рекомендації на основі задач."""
        if not tasks:
            return "Немає завдань для аналізу."

        recommendations = []
        for task in tasks:
            task_id, title, description, deadline, completed, priority = task
            prompt = (
                f"Завдання: \"{title}\"\n"
                f"Опис: {description}\n"
                f"Дедлайн: {deadline}\n"
                f"Пріоритет: {priority}\n\n"
                "Як організувати час? Як спростити задачу? Як відстежити своєчасність виконання?"
            )
            response = self.query(prompt)

            if "error" in response:
                recommendations.append(f"Помилка для '{title}': {response['error']}")
                continue

            generated_text = None
            if isinstance(response, list) and response and 'generated_text' in response[0]:
                generated_text = response[0]['generated_text']

            if generated_text:
                recommendations.append(f"Завдання: {title}\nРекомендація: {generated_text}\n")
            else:
                recommendations.append(f"Завдання: {title}\nРекомендація: (Текст не знайдено)\n")

        return "\n".join(recommendations)


class TaskManager:
    """Клас для управління базою даних завдань."""

    def __init__(self):
        self.db_name = "tasks.db"
        self.tasks = []
        self.create_db()

    def create_db(self):
        """Створює базу даних, якщо вона не існує."""
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
        """Завантажує задачі з бази."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, deadline, completed, priority FROM tasks")
        self.tasks = cursor.fetchall()
        conn.close()

    def add_task(self, title, description, deadline, priority):
        """Додає нову задачу до бази."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, description, deadline, priority)
            VALUES (?, ?, ?, ?)
        """, (title, description, deadline, priority))
        conn.commit()
        conn.close()

    def mark_task_completed(self, task_id):
        """Позначає задачу як виконану."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    def delete_task(self, task_id):
        """Видаляє задачу з бази."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()


class TaskApp:
    """Інтерфейс Tkinter для роботи з задачами."""

    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Task Manager with AI Suggestions")
        self.manager = TaskManager()
        self.t5 = T5Helper()

        self.title_label = tk.Label(self.root, text="Назва завдання")
        self.title_label.pack(padx=10, pady=5)
        self.title_entry = tk.Entry(self.root, width=40)
        self.title_entry.pack(padx=10, pady=5)

        self.desc_label = tk.Label(self.root, text="Опис завдання")
        self.desc_label.pack(padx=10, pady=5)
        self.desc_entry = tk.Entry(self.root, width=40)
        self.desc_entry.pack(padx=10, pady=5)

        self.deadline_label = tk.Label(self.root, text="Дедлайн (YYYY-MM-DD HH:MM)")
        self.deadline_label.pack(padx=10, pady=5)
        self.deadline_entry = tk.Entry(self.root, width=40)
        self.deadline_entry.pack(padx=10, pady=5)

        self.priority_label = tk.Label(self.root, text="Пріоритет (1-5)")
        self.priority_label.pack(padx=10, pady=5)
        self.priority_entry = tk.Entry(self.root, width=40)
        self.priority_entry.pack(padx=10, pady=5)

        self.add_button = tk.Button(self.root, text="Додати завдання", command=self.add_task)
        self.add_button.pack(padx=10, pady=10)

        self.suggestions_button = tk.Button(self.root, text="Отримати рекомендації", command=self.get_ai_suggestions)
        self.suggestions_button.pack(padx=10, pady=10)

        self.tasks_label = tk.Label(self.root, text="Список завдань")
        self.tasks_label.pack(padx=10, pady=5)
        self.tasks_listbox = tk.Listbox(self.root, width=80, height=10)
        self.tasks_listbox.pack(padx=10, pady=10)

        self.mark_completed_button = tk.Button(self.root, text="Позначити як виконане", command=self.mark_task_completed)
        self.mark_completed_button.pack(padx=10, pady=5)

        self.delete_button = tk.Button(self.root, text="Видалити завдання", command=self.delete_task)
        self.delete_button.pack(padx=10, pady=5)

        self.load_tasks()

    def load_tasks(self):
        """Оновлює список задач."""
        self.manager.load_tasks()
        self.tasks_listbox.delete(0, tk.END)
        for task in self.manager.tasks:
            task_id, title, _, deadline, completed, priority = task
            display_text = f"{task_id}: {title} (Пріоритет: {priority}, Дедлайн: {deadline})"
            if completed == 1:
                display_text += " - Виконано"
            self.tasks_listbox.insert(tk.END, display_text)

    def add_task(self):
        """Додає задачу з інтерфейсу."""
        title = self.title_entry.get()
        description = self.desc_entry.get()
        deadline = self.deadline_entry.get()
        try:
            priority = int(self.priority_entry.get())
            if not 1 <= priority <= 5:
                raise ValueError
        except ValueError:
            messagebox.showerror("Помилка", "Пріоритет повинен бути числом від 1 до 5.")
            return

        self.manager.add_task(title, description, deadline, priority)
        self.load_tasks()
        self.clear_entries()

    def get_ai_suggestions(self):
        """Отримує рекомендації на основі задач."""
        suggestions = self.t5.generate_suggestions(self.manager.tasks)
        messagebox.showinfo("Рекомендації", suggestions)

    def mark_task_completed(self):
        """Позначає обрану задачу як виконану."""
        try:
            selected_index = self.tasks_listbox.curselection()[0]
            task_id = self.manager.tasks[selected_index][0]
            self.manager.mark_task_completed(task_id)
            self.load_tasks()
        except IndexError:
            messagebox.showerror("Помилка", "Будь ласка, виберіть завдання.")

    def delete_task(self):
        """Видаляє обрану задачу."""
        try:
            selected_index = self.tasks_listbox.curselection()[0]
            task_id = self.manager.tasks[selected_index][0]
            self.manager.delete_task(task_id)
            self.load_tasks()
        except IndexError:
            messagebox.showerror("Помилка", "Будь ласка, виберіть завдання.")

    def clear_entries(self):
        """Очищає поля введення."""
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()
