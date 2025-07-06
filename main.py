import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import font as tkfont


class RussianTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Список дел")
        self.root.geometry("450x550")
        self.root.resizable(False, False)

        # Настройки стиля
        self.bg_color = "#f8f9fa"
        self.entry_bg = "#ffffff"
        self.button_color = "#4285f4"
        self.delete_color = "#ea4335"
        self.text_color = "#202124"
        self.completed_color = "#80868b"

        # Шрифты
        self.title_font = tkfont.Font(family="Arial", size=16, weight="bold")
        self.task_font = tkfont.Font(family="Arial", size=12)
        self.button_font = tkfont.Font(family="Arial", size=10)

        self.data_file = "todo_data.json"
        self.tasks = []
        self.sort_by_status = False
        self.drag_data = {"item": None, "index": None}

        self.load_tasks()
        self.create_widgets()
        self.setup_drag_and_drop()

    def setup_drag_and_drop(self):
        """Настройка перетаскивания задач"""
        self.task_list.bind("<Button-1>", self.drag_start)
        self.task_list.bind("<B1-Motion>", self.drag_motion)
        self.task_list.bind("<ButtonRelease-1>", self.drag_end)

    def drag_start(self, event):
        """Начало перетаскивания"""
        self.drag_data["item"] = self.task_list.nearest(event.y)
        self.drag_data["index"] = self.task_list.nearest(event.y)

    def drag_motion(self, event):
        """Процесс перетаскивания"""
        current_item = self.task_list.nearest(event.y)
        if current_item != self.drag_data["item"]:
            self.task_list.selection_clear(0, tk.END)
            self.task_list.selection_set(current_item)
            self.task_list.see(current_item)

    def drag_end(self, event):
        """Завершение перетаскивания"""
        end_index = self.task_list.nearest(event.y)
        if self.drag_data["index"] is not None and end_index != self.drag_data["index"]:
            # Получаем оригинальные индексы с учетом сортировки
            if self.sort_by_status:
                sorted_tasks = sorted(self.tasks, key=lambda x: x["completed"])
                task_to_move = sorted_tasks[self.drag_data["index"]]
                original_start = self.tasks.index(task_to_move)
                task_at_end = sorted_tasks[end_index]
                original_end = self.tasks.index(task_at_end)
            else:
                original_start = self.drag_data["index"]
                original_end = end_index

            # Перемещаем задачу
            task = self.tasks.pop(original_start)
            self.tasks.insert(original_end, task)
            self.save_tasks()
            self.update_task_list()

        self.drag_data["item"] = None
        self.drag_data["index"] = None

    def load_tasks(self):
        """Загрузка задач из файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []

    def save_tasks(self):
        """Сохранение задач в файл"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)

    def create_widgets(self):
        """Создание интерфейса"""
        # Главный контейнер
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        tk.Label(
            main_frame,
            text="СПИСОК ДЕЛ",
            bg=self.bg_color,
            fg=self.text_color,
            font=self.title_font
        ).pack(pady=(0, 15))

        # Поле ввода и кнопки
        input_frame = tk.Frame(main_frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, pady=(0, 15))

        self.task_entry = tk.Entry(
            input_frame,
            bg=self.entry_bg,
            fg=self.text_color,
            font=self.task_font,
            relief=tk.FLAT,
            width=30
        )
        self.task_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.task_entry.insert(0, "Добавьте задачу")
        self.task_entry.bind("<FocusIn>", self.clear_placeholder)

        add_btn = tk.Button(
            input_frame,
            text="+",
            command=self.add_task,
            bg=self.button_color,
            fg="white",
            font=self.title_font,
            relief=tk.FLAT,
            bd=0,
            width=3,
            pady=0
        )
        add_btn.pack(side=tk.LEFT)

        # Кнопка сортировки (компактная)
        sort_btn = tk.Button(
            main_frame,
            text="⇅",
            command=self.toggle_sort,
            bg="#34a853",
            fg="white",
            font=self.title_font,
            relief=tk.FLAT,
            bd=0,
            width=3,
            pady=0
        )
        sort_btn.pack(anchor=tk.E, pady=(0, 10))

        # Список задач
        self.task_list = tk.Listbox(
            main_frame,
            bg="white",
            fg=self.text_color,
            selectbackground=self.button_color,
            selectforeground="white",
            font=self.task_font,
            height=15,
            selectmode=tk.SINGLE,
            borderwidth=0,
            highlightthickness=0,
            activestyle="none"
        )
        self.task_list.pack(fill=tk.BOTH, expand=True)
        self.update_task_list()

        # Кнопки действий
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=(15, 0))

        tk.Button(
            btn_frame,
            text="✓",
            command=self.toggle_task,
            bg=self.button_color,
            fg="white",
            font=self.title_font,
            relief=tk.FLAT,
            bd=0,
            width=3,
            pady=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="✏",
            command=self.edit_task,
            bg=self.button_color,
            fg="white",
            font=self.title_font,
            relief=tk.FLAT,
            bd=0,
            width=3,
            pady=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🗑",
            command=self.delete_task,
            bg=self.delete_color,
            fg="white",
            font=self.title_font,
            relief=tk.FLAT,
            bd=0,
            width=3,
            pady=0
        ).pack(side=tk.LEFT, padx=5)

    def clear_placeholder(self, event):
        """Очистка подсказки в поле ввода"""
        if self.task_entry.get() == "Добавьте задачу":
            self.task_entry.delete(0, tk.END)

    def update_task_list(self):
        """Обновление списка задач"""
        self.task_list.delete(0, tk.END)

        # Сортировка при необходимости
        tasks_to_show = sorted(self.tasks, key=lambda x: x["completed"]) if self.sort_by_status else self.tasks

        for task in tasks_to_show:
            status = "✓" if task["completed"] else "[ ]"
            color = self.completed_color if task["completed"] else self.text_color
            self.task_list.insert(tk.END, f"{status} {task['text']}")
            self.task_list.itemconfig(tk.END, fg=color)

    def toggle_sort(self):
        """Переключение режима сортировки"""
        self.sort_by_status = not self.sort_by_status
        self.update_task_list()
        messagebox.showinfo("Сортировка",
                            "Сортировка по статусу включена" if self.sort_by_status
                            else "Сортировка по статусу выключена")

    def add_task(self):
        """Добавление новой задачи"""
        task_text = self.task_entry.get().strip()
        if task_text and task_text != "Добавьте задачу":
            self.tasks.append({
                "text": task_text,
                "completed": False
            })
            self.save_tasks()
            self.update_task_list()
            self.task_entry.delete(0, tk.END)
            messagebox.showinfo("Успех", "Задача добавлена!")
        else:
            messagebox.showwarning("Ошибка", "Введите текст задачи!")

    def toggle_task(self):
        """Изменение статуса задачи"""
        try:
            index = self.task_list.curselection()[0]
            if self.sort_by_status:
                # Находим оригинальный индекс с учетом сортировки
                sorted_tasks = sorted(self.tasks, key=lambda x: x["completed"])
                task_text = sorted_tasks[index]["text"]
                original_index = next(i for i, t in enumerate(self.tasks) if t["text"] == task_text)
                self.tasks[original_index]["completed"] = not self.tasks[original_index]["completed"]
            else:
                self.tasks[index]["completed"] = not self.tasks[index]["completed"]

            self.save_tasks()
            self.update_task_list()
        except IndexError:
            messagebox.showwarning("Ошибка", "Выберите задачу!")

    def edit_task(self):
        """Редактирование задачи"""
        try:
            index = self.task_list.curselection()[0]
            if self.sort_by_status:
                sorted_tasks = sorted(self.tasks, key=lambda x: x["completed"])
                task_text = sorted_tasks[index]["text"]
                original_index = next(i for i, t in enumerate(self.tasks) if t["text"] == task_text)
                current_task = self.tasks[original_index]
            else:
                current_task = self.tasks[index]

            new_text = simpledialog.askstring(
                "Редактирование",
                "Измените задачу:",
                initialvalue=current_task["text"],
                parent=self.root
            )

            if new_text and new_text != current_task["text"]:
                current_task["text"] = new_text
                self.save_tasks()
                self.update_task_list()

        except IndexError:
            messagebox.showwarning("Ошибка", "Выберите задачу!")

    def delete_task(self):
        """Удаление задачи"""
        try:
            index = self.task_list.curselection()[0]
            if self.sort_by_status:
                sorted_tasks = sorted(self.tasks, key=lambda x: x["completed"])
                task_text = sorted_tasks[index]["text"]
                original_index = next(i for i, t in enumerate(self.tasks) if t["text"] == task_text)
                del self.tasks[original_index]
            else:
                del self.tasks[index]

            self.save_tasks()
            self.update_task_list()
        except IndexError:
            messagebox.showwarning("Ошибка", "Выберите задачу!")


if __name__ == "__main__":
    root = tk.Tk()
    app = RussianTodoApp(root)
    root.mainloop()