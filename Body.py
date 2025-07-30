import json
import os
import threading
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox, filedialog

from ApplicationDataChecker import main as application_data_checker_main
from AuthorVerificationProgram import main as author_main
from CNCFileCheckingProgram import mainCNCFileCheckingProgram, today


class GUIdirManager:
    """GUI версия менеджера директорий"""

    def __init__(self, parent):
        self.parent = parent
        self.directories = {}
        self.CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".CNCDirCheckingProgram")
        self.CONFIG_FILE_DIR = os.path.join(self.CONFIG_DIR, "directories.json")
        self.create_config_dir()
        self.load_directories()

    def create_config_dir(self):
        if not os.path.exists(self.CONFIG_DIR):
            os.makedirs(self.CONFIG_DIR)

    def load_directories(self):
        if not os.path.exists(self.CONFIG_FILE_DIR):
            self.directories = {}
            return
        try:
            with open(self.CONFIG_FILE_DIR, 'r', encoding='utf-8') as f:
                self.directories = json.load(f)
        except Exception:
            self.directories = {}

    def save_directories(self):
        try:
            with open(self.CONFIG_FILE_DIR, 'w', encoding='utf-8') as f:
                json.dump(self.directories, f, ensure_ascii=False, indent=4)
            return True
        except Exception:
            return False

    def get_directories_list(self):
        result = []
        for name, path in self.directories.items():
            path = path.replace("\\", "/")
            result.append(path)
        return result

    def add_directory(self, name, path):
        if name in self.directories:
            return False
        self.directories[name] = path
        return self.save_directories()

    def delete_directory(self, index):
        items = list(self.directories.items())
        if 0 <= index < len(items):
            key_to_delete = items[index][0]
            del self.directories[key_to_delete]
            return self.save_directories()
        return False

    def open_config_file(self):
        if os.path.exists(self.CONFIG_FILE_DIR):
            webbrowser.open(self.CONFIG_FILE_DIR)


class DirectoryManagerGUI:
    """Окно управления директориями"""

    def __init__(self, parent, dir_manager):
        self.window = tk.Toplevel(parent)
        self.window.title("Управление директориями")
        self.window.geometry("600x400")
        self.window.transient(parent)
        self.window.grab_set()

        self.dir_manager = dir_manager

        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        # Фрейм для добавления директории
        add_frame = ttk.LabelFrame(self.window, text="Добавить директорию", padding=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(add_frame, text="Имя:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.name_entry = ttk.Entry(add_frame, width=20)
        self.name_entry.grid(row=0, column=1, padx=(0, 10))

        ttk.Label(add_frame, text="Путь:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.path_entry = ttk.Entry(add_frame, width=30)
        self.path_entry.grid(row=0, column=3, padx=(0, 5))

        browse_btn = ttk.Button(add_frame, text="Обзор", command=self.browse_directory)
        browse_btn.grid(row=0, column=4, padx=(0, 5))

        add_btn = ttk.Button(add_frame, text="Добавить", command=self.add_directory)
        add_btn.grid(row=0, column=5)

        # Фрейм для списка директорий
        list_frame = ttk.LabelFrame(self.window, text="Сохранённые директории", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Список директорий
        self.tree = ttk.Treeview(list_frame, columns=("name", "path"), show="headings", height=10)
        self.tree.heading("name", text="Имя")
        self.tree.heading("path", text="Путь")
        self.tree.column("name", width=150)
        self.tree.column("path", width=400)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", padx=10, pady=5)

        delete_btn = ttk.Button(button_frame, text="Удалить", command=self.delete_directory)
        delete_btn.pack(side="left", padx=(0, 5))

        open_file_btn = ttk.Button(button_frame, text="Открыть файл с директориями", command=self.open_config_file)
        open_file_btn.pack(side="left", padx=(0, 5))

        close_btn = ttk.Button(button_frame, text="Закрыть", command=self.window.destroy)
        close_btn.pack(side="right")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, os.path.basename(directory))

    def add_directory(self):
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()

        if not os.path.isdir(path):
            messagebox.showerror("Ошибка", "Указанный путь не существует или не является директорией")
            return
        if not name or not path:
            messagebox.showwarning("Предупреждение", "Пожалуйста, заполните все поля")
            return

        if self.dir_manager.add_directory(name, path):
            self.name_entry.delete(0, tk.END)
            self.path_entry.delete(0, tk.END)
            self.refresh_list()
            messagebox.showinfo("Успех", "Директория успешно добавлена")
        else:
            messagebox.showerror("Ошибка", "Директория с таким именем уже существует")

    def delete_directory(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите директорию для удаления")
            return

        index = self.tree.index(selected[0])
        if self.dir_manager.delete_directory(index):
            self.refresh_list()
            messagebox.showinfo("Успех", "Директория успешно удалена")
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить директорию")

    def open_config_file(self):
        self.dir_manager.open_config_file()

    def refresh_list(self):
        # Очистка списка
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполнение списка
        for name, path in self.dir_manager.directories.items():
            self.tree.insert("", "end", values=(name, path))


class MainCNCprogrammeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CNCFileCheckingProgram")
        self.root.geometry("700x650")
        self.root.resizable(True, True)

        # Менеджер директорий
        self.dir_manager = GUIdirManager(self.root)

        # Переменные
        self.choseUserProgramme = tk.IntVar()
        self.choseUserChangeDir = tk.BooleanVar()
        self.choseUserUseSaveDir = tk.BooleanVar()
        self.custom_output_file = tk.StringVar()

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Фрейм для выбора варианта программы
        program_frame = ttk.LabelFrame(self.root, text="Выберите вариант работы программы", padding=10)
        program_frame.pack(fill="x", padx=10, pady=5)

        # Радиокнопки для выбора варианта
        programs = [
            ("1. Работает только программа обработки директорий", 1),
            ("2. Работают программа обработки директорий и программа создания сводных таблиц", 2),
            ("3. Работает программа отображения авторов nc и h файлов", 3),
            ("4. Работают программы обработки директорий и отображения авторов", 4),
            ("5. Работают все программы", 5)
        ]

        for text, value in programs:
            rb = ttk.Radiobutton(program_frame, text=text, variable=self.choseUserProgramme, value=value)
            rb.pack(anchor="w", pady=2)

        # Установка значения по умолчанию
        self.choseUserProgramme.set(1)

        # Фрейм для настроек директорий
        dir_frame = ttk.LabelFrame(self.root, text="Настройки директорий", padding=10)
        dir_frame.pack(fill="x", padx=10, pady=5)

        # Чекбоксы
        change_dir_cb = ttk.Checkbutton(dir_frame, text="Изменить сохранённые репозитории",
                                        variable=self.choseUserChangeDir,
                                        command=self.open_directory_manager)
        change_dir_cb.pack(anchor="w", pady=2)

        use_save_dir_cb = ttk.Checkbutton(dir_frame, text="Использовать сохранённые репозитории",
                                          variable=self.choseUserUseSaveDir)
        use_save_dir_cb.pack(anchor="w", pady=2)

        # Фрейм для имени файла
        file_frame = ttk.LabelFrame(self.root, text="Имя выходного файла (необязательно)", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)

        # Поле ввода для имени файла
        self.output_file_entry = ttk.Entry(file_frame, textvariable=self.custom_output_file)
        self.output_file_entry.pack(fill="x", pady=2)

        # Кнопка для выбора файла
        browse_btn = ttk.Button(file_frame, text="Выбрать файл", command=self.browse_file)
        browse_btn.pack(pady=5)

        # Прогресс-бар
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(fill="x", pady=2)

        self.progress_label = ttk.Label(progress_frame, text="Готово")
        self.progress_label.pack()

        # Кнопка запуска
        run_btn = ttk.Button(self.root, text="ЗАПУСТИТЬ ПРОГРАММУ", command=self.start_program)
        run_btn.pack(pady=10)

        # Текстовое поле для логов
        log_frame = ttk.LabelFrame(self.root, text="Лог выполнения", padding=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = tk.Text(log_frame, height=12, wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка очистки лога
        clear_log_btn = ttk.Button(self.root, text="Очистить лог", command=self.clear_log)
        clear_log_btn.pack(pady=5)

    def open_directory_manager(self):
        if self.choseUserChangeDir.get():
            DirectoryManagerGUI(self.root, self.dir_manager)

    def browse_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Выберите файл для сохранения"
        )
        if filename:
            self.custom_output_file.set(filename)

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def start_program(self):
        """Запуск программы в отдельном потоке"""
        self.progress.start()
        self.progress_label.config(text="Выполнение...")
        thread = threading.Thread(target=self.run_program)
        thread.daemon = True
        thread.start()

    def program_finished(self):
        """Вызывается по завершении программы"""
        self.progress.stop()
        self.progress_label.config(text="Готово")

    def get_output_filename(self):
        output_file = self.custom_output_file.get().strip()
        if not output_file:
            output_file = f"BD_CNCprog_{today}"
        if not output_file.endswith(".xlsx"):
            output_file += ".xlsx"
        return output_file

    def run_program(self):
        try:
            # Получаем значения
            choseUserProgramme = self.choseUserProgramme.get()
            choseUserUseSaveDir = self.choseUserUseSaveDir.get()
            output_file = self.get_output_filename()

            self.log_message(f"Запуск программы. Вариант: {choseUserProgramme}")
            self.log_message(f"Выходной файл: {output_file}")

            # Выполнение программы в зависимости от выбора
            if choseUserProgramme == 1:
                self.log_message("Выполнение программы обработки директорий...")
                if choseUserUseSaveDir:
                    directories = self.dir_manager.get_directories_list()
                    result = mainCNCFileCheckingProgram(directories, 1, 0)
                else:
                    result = mainCNCFileCheckingProgram(list(), 0, 0)
                self.log_message("Программа завершена!")

            elif choseUserProgramme == 2:
                self.log_message("Выполнение программы обработки директорий и создания сводных таблиц...")
                if choseUserUseSaveDir:
                    directories = self.dir_manager.get_directories_list()
                    output_file = mainCNCFileCheckingProgram(directories, 1, 1)
                else:
                    output_file = mainCNCFileCheckingProgram(list(), 0, 1)

                self.log_message("Программа CNCFileCheckingProgram завершена. Создание сводной таблицы...")
                full_output_path = application_data_checker_main(output_file)
                self.log_message("Обработка завершена. Лист 'ДЕ по станкам' создан.")

                # Предложение открыть файл в основном потоке
                self.root.after(0, lambda: self.ask_open_file(os.path.basename(full_output_path)))

            elif choseUserProgramme == 3:
                self.log_message("Выполнение программы отображения авторов...")
                author_main(output_file)
                self.log_message("Программа завершена!")

            elif choseUserProgramme == 4:
                self.log_message("Выполнение программ обработки директорий и отображения авторов...")
                if choseUserUseSaveDir:
                    directories = self.dir_manager.get_directories_list()
                    mainCNCFileCheckingProgram(directories, 1, 1)
                else:
                    mainCNCFileCheckingProgram(list(), 0, 1)
                author_main(output_file)
                self.log_message("Программы завершены!")

            else:  # choseUserProgramme == 5
                self.log_message("Выполнение всех программ...")
                if choseUserUseSaveDir:
                    directories = self.dir_manager.get_directories_list()
                    output_file = mainCNCFileCheckingProgram(directories, 1, 1)
                else:
                    output_file = mainCNCFileCheckingProgram(list(), 0, 1)

                self.log_message("Программа CNCFileCheckingProgram завершена. Создание сводной таблицы...")
                full_output_path = application_data_checker_main(output_file)
                self.log_message("Обработка завершена. Лист 'ДЕ по станкам' создан.")

                author_main(output_file)

                # Предложение открыть файл в основном потоке
                self.root.after(0, lambda: self.ask_open_file(os.path.basename(full_output_path)))

            self.log_message("Все операции завершены!")
            self.root.after(0, lambda: messagebox.showinfo("Успех", "Программа выполнена успешно!"))

        except Exception as e:
            error_msg = f"Ошибка выполнения: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Ошибка", error_msg))
        finally:
            self.root.after(0, self.program_finished)

    def ask_open_file(self, file_path):
        """Запрос на открытие файла в основном потоке"""
        if messagebox.askyesno("Открыть файл", "Обработка завершена. Хотите открыть файл?"):
            webbrowser.open(file_path)



def main():
    root = tk.Tk()
    app = MainCNCprogrammeGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
