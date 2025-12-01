import json
import os
import sys
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

import plyer

from ApplicationDataChecker import main as application_data_checker_main
from AuthorVerificationProgram import main as author_main
from CNCFileCheckingProgram import mainCNCFileCheckingProgram, today
from useJson import JsonSave, JsonConfig


def seconds_to_minutes_seconds(seconds):
    """
    Преобразует секунды в минуты и секунды.

    Args:
      seconds: Целое число, представляющее секунды.

    Returns:
      Кортеж из двух целых чисел: (минуты, секунды).
    """
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return minutes, remaining_seconds


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


change_dir_cb_bool = 0


class GUIdirManager:
    """GUI версия менеджера директорий"""

    def __init__(self, parent):
        self.parent = parent
        self.directories = {}
        self.CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".CNCDirCheckingProgram")
        self.CONFIG_FILE_DIR = os.path.join(self.CONFIG_DIR, "directories.json")
        self.create_config_dir()
        self.load_directories()

    def returnNameFile(self):
        return self.CONFIG_FILE_DIR

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


class FileNameManagerGUI:
    """Окно управления директориями"""

    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Управление выходным файлом")
        self.window.geometry("600x80+400+150")
        self.window.resizable(False, False)

        # Установка иконки
        try:
            icon_path = resource_path("gear.ico")
            self.window.iconbitmap(icon_path)
        except Exception as e:
            print(f"Не удалось установить иконку: {e}")

    def returnRoot(self):
        return self.window


class DirectoryManagerGUI:
    """Окно управления директориями"""

    def __init__(self, parent, dir_manager):
        self.window = tk.Toplevel(parent)
        self.window.title("Управление директориями")
        self.window.geometry("600x400")
        self.window.resizable(False, False)

        # Установка иконки
        try:
            icon_path = resource_path("dirBook.ico")
            self.window.iconbitmap(icon_path)
        except Exception as e:
            print(f"Не удалось установить иконку: {e}")

        self.window.transient(parent)
        self.window.grab_set()
        self.dir_manager = dir_manager
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        global change_dir_cb_bool
        change_dir_cb_bool = not change_dir_cb_bool
        # Фрейм для добавления директории
        add_frame = ttk.LabelFrame(self.window, text="Добавить директорию", padding=10)
        add_frame.pack(fill="x", padx=10, pady=5)
        Label(add_frame, text="Имя:").grid(row=0, column=0, sticky="w", padx=(0, 5))
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

def send_notification(title, message, settime=15, file_path=""):
    plyer.notification.notify(
        title=title,
        message=message,
        app_name="ToolCheckerProgram",
        timeout=settime
    )

    if file_path and os.path.exists(file_path) and file_path != "":
        os.startfile(file_path)
# --- КОНЕЦ ВСТАВКИ КЛАССОВ ---

class MainCNCprogrammeGUI:
    def __init__(self, root):

        self.maxDistanceY = 105
        self.file_frame_bool = 1
        global change_dir_cb_bool
        self.distanceY = 660
        self.distanceMinY = 152
        self.root = root
        self.root.title("CNCFileCheckingProgram")
        self.root.geometry(f"700x{self.distanceY}")
        self.root.resizable(False, False)
        self.operating_mode_var = StringVar(value="2")
        self.selection_gui_var = StringVar(value="Включён")
        self.selection_gui_bool = True

        # Установка иконки
        try:
            icon_path = resource_path("iconca.ico")
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Не удалось установить иконку: {e}")

        # Менеджер директорий
        self.dir_manager = GUIdirManager(self.root)
        # Переменные
        self.log_frame_Bool = 0

        self.timerWorkProg = StringVar(value=f"Время работы программы: Нет")
        self.timerWorkProgBool = 1
        self.run_cnc_checking = tk.BooleanVar()
        self.run_data_checker = tk.BooleanVar()
        self.run_author_verification = tk.BooleanVar()
        self.choseUserChangeDir = tk.BooleanVar()
        self.choseUserUseSaveDir = tk.BooleanVar()
        self.choseUserUseSaveDir = True
        self.custom_output_file = tk.StringVar()
        self.config_json = JsonConfig()

        main_menu = tk.Menu()
        # подменю настроек
        settings_menu = tk.Menu(tearoff=0)
        settings_menu.add_command(label="Отобразить ход программы", command=self.log_frame_command)
        settings_menu.add_command(label="Имя файла", command=self.file_frame_command)
        settings_menu.add_command(label="Run config json", command=self.run_config_file_json)
        settings_menu.add_command(label=f"Графический интерфейс", command=self.selection_gui_command)

        main_menu.add_cascade(label="Settings", menu=settings_menu)
        main_menu.add_cascade(label="Saved Directories", command=self.open_directory_manager)
        main_menu.add_cascade(label="Help", command=lambda: self.show_program_info(self.root))
        self.root.config(menu=main_menu)

        # Создание интерфейса
        self.create_widgets()

    def selection_gui_command(self):
        if self.selection_gui_bool:
            self.selection_gui_var.set("Выключен")
        else:
            self.selection_gui_var.set("Включён")
        self.selection_gui_bool = not self.selection_gui_bool

    def run_config_file_json(self):
        webbrowser.open(self.config_json.return_file_path())


    def show_program_info(self, parent=None):
        """
        Отображает информацию о программе GuiCNCFileCheckingProgram в отдельном окне

        Args:
            parent: Родительское окно (опционально)
        """

        # Создаем Toplevel окно
        info_window = tk.Toplevel(parent)
        info_window.title("Информация о программе")
        info_window.geometry("600x500+100+650")
        info_window.resizable(False, False)
        info_window.overrideredirect(True)

        # Установка иконки
        try:
            icon_path = resource_path("gear.ico")
            info_window.iconbitmap(icon_path)
        except Exception as e:
            print(f"Не удалось установить иконку: {e}")

        # Центрируем окно относительно родительского окна
        if parent:
            parent_x = parent.winfo_x()
            parent_y = parent.winfo_y()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()

            x = parent_x + (parent_width // 2) - (600 // 2)
            y = parent_y + (parent_height // 2) - (500 // 2)
            if x < 0 or y < 0:
                info_window.geometry(f"600x500")
            else:
                info_window.geometry(f"600x500+{x}+{y}")

        info_window.lift()
        info_window.focus_force()

        # Создаем основной фрейм
        main_frame = ttk.Frame(info_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.bind('<B1-Motion>', lambda e: info_window.geometry('+{0}+{1}'.format(e.x_root, e.y_root)))

        # Заголовок
        title_label = ttk.Label(
            main_frame,
            text="GuiCNCFileCheckingProgram",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Описание программы
        description_text = "Версия программы CNCFileCheckingProgram с графическим интерфейсом и ограниченным функционалом"
        description_label = ttk.Label(
            main_frame,
            text=description_text,
            wraplength=550,
            justify=tk.LEFT
        )
        description_label.pack(pady=(0, 15))

        # Создаем Notebook для вкладок
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка "Основные компоненты"
        components_frame = ttk.Frame(notebook)
        notebook.add(components_frame, text="Основные компоненты")

        components_text = """• Программа обработки директорий - Основа CNCFileCheckingProgram. Формирует Excel-таблицу с информацией о директориях, содержащих ДСЕ, их содержимом и прямыми ссылками на файлы.

    • Программа создания сводной таблицы - Создаёт лист «ДСЕ по станкам», в котором отображаются данные о ДСЕ и станках, на которых они используются. Также указывается дата последнего изменения файла.

    • Программа отображения авторов NC- и H-файлов - Позволяет просматривать информацию об авторах NC- и H-файлов."""

        components_text_widget = ScrolledText(
            components_frame,
            wrap=tk.WORD,
            width=60,
            height=15,
            font=("Arial", 10)
        )
        components_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        components_text_widget.insert(tk.END, components_text)
        components_text_widget.config(state=tk.DISABLED)

        # Вкладка "Меню"
        menu_frame = ttk.Frame(notebook)
        notebook.add(menu_frame, text="Меню")

        # Создаем Treeview для отображения структуры меню
        menu_tree = ttk.Treeview(menu_frame, columns=("Описание"), show="tree headings", height=15)
        menu_tree.heading("#0", text="Пункт меню")
        menu_tree.heading("Описание", text="Описание")
        menu_tree.column("#0", width=150)
        menu_tree.column("Описание", width=350)

        # Добавляем данные в дерево
        settings = menu_tree.insert("", "end", text="1. Settings", open=True)
        menu_tree.insert(settings, "end", text="1. Отображать ход выполнения",
                         values=("Включает вывод логов и процесса выполнения программы",))
        menu_tree.insert(settings, "end", text="2. Имя файла",
                         values=("Позволяет просмотреть или задать имя исполняемого файла",))
        menu_tree.insert(settings, "end", text="3. Run config json",
                         values=("Открывает конфигурационный JSON-файл с указанием директорий",))

        saved_dirs = menu_tree.insert("", "end", text="2. Saved Directories",
                                      values=("Просмотр и настройка списка сохранённых директорий",))
        help_item = menu_tree.insert("", "end", text="3. Help", values=("help"))

        menu_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Кнопка закрытия
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        close_button = ttk.Button(
            button_frame,
            text="Закрыть",
            command=info_window.destroy
        )
        close_button.pack(side=tk.RIGHT)

        # Фокус на окно
        info_window.focus_set()

    def log_frame_command(self):
        if self.log_frame_Bool:
            self.log_frame.place_forget()
            self.progress_label.grid_remove()
            self.root.geometry(f"700x{self.distanceMinY}")

        else:
            self.root.geometry(f"700x{self.distanceY}")
            distanceY = 180
            self.progress_label.grid(row=1, column=0)
            self.log_frame.place(x=10, y=distanceY, height=650 - distanceY, width=680)
        self.log_frame_Bool = not self.log_frame_Bool

    def open_directory_manager(self):
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
        print( self.operating_mode_var.get())
        if  "0" == self.operating_mode_var.get():
            messagebox.showwarning("Внимание", "Перед началом выберете режим работы!")
            return
        elif  self.operating_mode_var.get() == "2":
            self.file_frame_command()
            if self.timerWorkProgBool:
                self.timer_label.place_forget()
                self.timerWorkProgBool = not self.timerWorkProgBool
                # self добавить таймер удаление
            self.progress.grid()
            self.progress_label.grid()
            """Запуск программы в отдельном потоке"""
            # Проверяем, что выбрана хотя бы одна программа
            if not any([self.run_cnc_checking.get(), self.run_data_checker.get(), self.run_author_verification.get()]):
                messagebox.showwarning("Предупреждение", "Пожалуйста, выберите хотя бы одну программу для запуска")
                return
            self.progress["value"] = 0
            self.progress_label.config(text="Подготовка...")
            total_steps = sum([
                self.run_cnc_checking.get(),
                self.run_data_checker.get(),
                self.run_author_verification.get()
            ])
            thread = threading.Thread(target=lambda: self.run_program(total_steps))
            thread.daemon = True
            thread.start()


            send_notification("Программа завершена.",
                              f"Программа ToolCheckerProgram завершена, данные сохранены в файл: {self.config_json.getNameAutomaticallyFile()}.xlsx",
                              15,
                              f"{self.config_json.getPathAutomaticallyFile()}.xlsx"
                              )
        else:
            messagebox.showerror("Ошибка","Что то пошло не так при выборе режима работы")

    def update_progress(self, value, text):
        """Обновление прогресс-бара"""
        self.progress["value"] = value
        self.progress_label.config(text=text)
        self.root.update()

    def get_output_filename(self):
        output_file = self.custom_output_file.get().strip()
        if not output_file:
            output_file = f"BD_CNCprog_{today}"
        if not output_file.endswith(".xlsx"):
            output_file += ".xlsx"
        return output_file

    def run_program(self, total_steps):
        try:
            # Получаем значения
            run_cnc = self.run_cnc_checking.get()
            run_data = self.run_data_checker.get()
            run_author = self.run_author_verification.get()

            output_file = self.get_output_filename()
            print("output_file", output_file)

            self.log_message(f"Запуск выбранных программ:")
            # countProg =0 # --- УДАЛЕНО --- Не используется
            if run_cnc:
                self.log_message("- Программа обработки директорий")
            if run_data:
                self.log_message("- Программа создания сводной таблицы")
            if run_author:
                self.log_message("- Программа отображения авторов")
            self.log_message(f"Выходной файл: {output_file}")

            # Выполнение программ в зависимости от выбора
            result_file = output_file
            current_step = 0  # Счетчик выполненных основных шагов (программ)

            start_time = time.time()

            """
            # Шаг 1: Программа обработки директорий
            """
            if run_cnc:
                segment_start_percent = (current_step / total_steps) * 100
                segment_size_percent = (1 / total_steps) * 100
                current_step += 1

                progress_text = f"Выполнение обработки директорий... ({current_step}/{total_steps})"
                self.root.after(0, lambda: self.update_progress(segment_start_percent, progress_text))
                self.log_message("Выполнение программы обработки директорий...")
                tracker = ProgressTracker(self, segment_start_percent, segment_size_percent)

                directories = self.dir_manager.get_directories_list()
                if not directories:
                    warning_msg = "Предупреждение: Выбрано использование сохраненных директорий, но список пуст. Пропуск обработки."
                    self.log_message(warning_msg)
                    self.root.after(0, lambda: self.update_progress(segment_start_percent + segment_size_percent,
                                                                    "Пропущено: Нет директорий"))
                    print("Я тут")
                else:
                    result_file = mainCNCFileCheckingProgram(directories, 1, 1 if run_data else 0, tracker, 1)
                    print(result_file)
                    if result_file is None:
                        print(result_file, "Программа обработки директорий не вернула имя файла.")
                        raise Exception("Программа обработки директорий не вернула имя файла.")

            """
            # Шаг 2: Программа создания сводных таблиц
            """
            if run_data:
                # Вычисляем сегмент для этой программы
                segment_start_percent = (current_step / total_steps) * 100
                segment_size_percent = (1 / total_steps) * 100
                current_step += 1

                progress_text = f"Создание сводных таблиц... ({current_step}/{total_steps})"
                self.root.after(0, lambda: self.update_progress(segment_start_percent, progress_text))
                self.log_message("Создание сводной таблицы...")
                if not run_cnc:
                    print()

                # Создаем новый трекер для этой программы
                tracker = ProgressTracker(self, segment_start_percent, segment_size_percent)

                try:
                    full_output_path = application_data_checker_main(output_file, tracker)
                    self.log_message("Обработка завершена. Лист 'ДСЕ по станкам' создан.")
                    # Обновляем прогресс до конца сегмента после завершения
                    self.root.after(0, lambda: self.update_progress(segment_start_percent + segment_size_percent,
                                                                    "Создание сводных таблиц завершено"))
                except Exception as e:
                    # Обработка ошибок внутри программы
                    error_msg = f"Ошибка в программе создания сводных таблиц: {str(e)}"
                    self.log_message(error_msg)
                    # Обновляем прогресс с сообщением об ошибке
                    self.root.after(0, lambda: self.update_progress(segment_start_percent + segment_size_percent,
                                                                    f"Ошибка в сводных таблицах: {type(e).__name__}"))
                    raise  # Перебрасываем исключение
            """
            # Шаг 3: Программа отображения авторов
            """
            if run_author:
                segment_start_percent = (current_step / total_steps) * 100
                segment_size_percent = (1 / total_steps) * 100
                current_step += 1

                progress_text = f"Отображение авторов... ({current_step}/{total_steps})"
                self.root.after(0, lambda: self.update_progress(segment_start_percent, progress_text))
                self.log_message("Выполнение программы отображения авторов...")

                tracker = ProgressTracker(self, segment_start_percent, segment_size_percent)

                try:
                    # --- ИСПРАВЛЕНО ---
                    # Передаем result_file и tracker в author_main
                    author_main(output_file, tracker)
                    self.log_message("Программа отображения авторов завершена!")
                    # Обновляем прогресс до конца сегмента после завершения
                    self.root.after(0, lambda: self.update_progress(segment_start_percent + segment_size_percent,
                                                                    "Отображение авторов завершено"))
                except Exception as e:
                    # Обработка ошибок внутри программы
                    error_msg = f"Ошибка в программе отображения авторов: {str(e)}"
                    self.log_message(error_msg)
                    # Обновляем прогресс с сообщением об ошибке
                    self.root.after(0, lambda: self.update_progress(segment_start_percent + segment_size_percent,
                                                                    f"Ошибка в отображении авторов: {type(e).__name__}"))
                    raise

            # Завершение
            self.root.after(0, lambda: self.update_progress(100, "Завершено!"))
            self.log_message("Все выбранные операции завершены!")
            self.progress.grid_remove()
            self.progress_label.grid_remove()
            file_to_open = result_file if result_file != output_file else output_file
            end_time = time.time()
            execution_time = end_time - start_time
            self.timerWorkProgBool = 1
            execution_time = str(execution_time)
            minutes, seconds = seconds_to_minutes_seconds(int(execution_time[:execution_time.index(".")]))
            self.timerWorkProg.set(f"Время работы программы: {minutes}мин {seconds}сек")
            self.timer_label.place(x=5, y=self.maxDistanceY, height=24)
            self.ask_open_file(file_to_open)

        except Exception as e:
            error_msg = f"Ошибка выполнения: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Ошибка", error_msg))
        finally:
            # Сброс прогресс-бара через 2 секунды
            self.root.after(2000, lambda: self.update_progress(0, "Готово"))

    def create_widgets(self):
        global change_dir_cb_bool

        offsetX = 5
        offsetY = 0

        maxDistanceY = self.maxDistanceY
        distanseY = 25

        # Фрейм для выбора программ
        program_frame = ttk.LabelFrame(self.root, text="Выберите программы для запуска:", padding=10)
        program_frame.place(x=offsetX, y=offsetY, height=100, width=330)

        # Чекбоксы для выбора программ
        cnc_cb = ttk.Checkbutton(program_frame, text="Программа обработки директорий",
                                 variable=self.run_cnc_checking)

        cnc_cb.place(x=offsetX, y=0)
        data_cb = ttk.Checkbutton(program_frame, text="Программа создания сводной таблицы",
                                  variable=self.run_data_checker)
        data_cb.place(x=offsetX, y=offsetY + distanseY)
        author_cb = ttk.Checkbutton(program_frame, text="Программа отображения авторов nc и h файлов",
                                    variable=self.run_author_verification)
        author_cb.place(x=offsetX, y=offsetY + distanseY * 2)

        operating_mode = ttk.LabelFrame(self.root, text="Выберите режим работы:", padding=10)
        operating_mode.place(x=offsetX+530, y=offsetY, height=100, width=160)

        operating_mode_chose = ttk.Radiobutton(operating_mode, text="Ничего",
                                                       value="0", variable=self.operating_mode_var)
        operating_mode_chose.grid(row=0,column=0,sticky="w")
        operating_mode_automatically = ttk.Radiobutton(operating_mode,text="Только различные",value="1", variable=self.operating_mode_var)
        operating_mode_automatically.grid(row=1,column=0,sticky="w")
        operating_mode_full = ttk.Radiobutton(operating_mode,text="Всё",value="2", variable=self.operating_mode_var)
        operating_mode_full.grid(row=2, column=0,sticky="w")

        # Установка значений по умолчанию
        self.run_cnc_checking.set(True)
        self.run_data_checker.set(False)
        self.run_author_verification.set(False)
        # Фрейм для настроек директорий
        dir_frame = ttk.LabelFrame(self.root, text="Настройки директорий", padding=10)
        dir_frame.pack(fill="x", padx=10, pady=5)

        # Прогресс-бар
        progress_frame = ttk.Frame(self.root)
        progress_frame.place(x=offsetX, y=maxDistanceY, height=60)
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=600,
                                        maximum=100)
        self.progress.place(x=5, y=self.maxDistanceY - 5)
        self.progress_label = ttk.Label(progress_frame, text="Готово")
        self.progress_label.grid(row=1, column=0)

        self.progress.grid_remove()
        self.progress_label.grid_remove()

        self.timer_label = Label(self.root, textvariable=self.timerWorkProg)
        self.timer_label.place(x=5, y=self.maxDistanceY - 1, height=24)
        self.timer_label.place_forget()

        # Кнопка запуска
        run_btn = ttk.Button(self.root, text="Начать", command=self.start_program)
        run_btn.place(x=615, y=maxDistanceY - 1, height=24)

        # Текстовое поле для логов
        self.log_frame = ttk.LabelFrame(self.root, text="Лог выполнения", padding=5)
        self.log_frame.place(x=5, y=168)
        self.log_text = tk.Text(self.log_frame, height=12, wrap="word")
        scrollbar = ttk.Scrollbar(self.log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        clear_log_btn = ttk.Button(self.log_text, text="Очистить лог", command=self.clear_log)
        clear_log_btn.pack(pady=5, anchor="e")
        self.log_frame.place_forget()

        self.root.geometry(f"700x{self.distanceMinY}")

    def file_frame_command(self):
        if self.file_frame_bool:
            classRoot = FileNameManagerGUI(self.root)
            root = classRoot.returnRoot()
            file_frame = ttk.LabelFrame(root, text="Имя выходного файла", padding=10)
            file_frame.pack(fill="x", padx=10, pady=5)

            # Поле ввода для имени файла
            self.output_file_entry = ttk.Entry(file_frame, textvariable=self.custom_output_file)
            self.output_file_entry.pack(fill="x", side="left", expand=True)
            output_file = f"BD_CNCprog_{today}"
            if not output_file.endswith(".xlsx"):
                output_file += ".xlsx"
            self.output_file_entry.delete(0, END)
            self.output_file_entry.insert(0, output_file)
            # Кнопка для выбора файла
            browse_btn = ttk.Button(file_frame, text="Выбрать файл", command=self.browse_file)
            browse_btn.pack(side="right", padx=(5, 0))
        self.file_frame_bool = not self.file_frame_bool

    def ask_open_file(self, file_path):
        """Запрос на открытие файла в основном потоке"""
        if messagebox.askyesno("Открыть файл", "Обработка завершена. Хотите открыть файл?"):
            # --- ИЗМЕНЕНО --- Проверяем file_path
            if file_path and os.path.exists(file_path):
                webbrowser.open(file_path)
            else:
                messagebox.showerror("Ошибка", f"Файл не найден: {file_path}")


class ProgressTracker:
    def __init__(self, gui_app, segment_start_percent=0, segment_size_percent=100):
        self.gui_app = gui_app
        # Процент, с которого начинается сегмент этой программы
        self.segment_start_percent = segment_start_percent
        # Размер сегмента этой программы в процентах (например, 33.33 для 1/3)
        self.segment_size_percent = segment_size_percent
        self.total_steps = 0
        self.current_step = 0

    def set_total(self, total_steps):
        """Устанавливает общее количество внутренних шагов для текущей программы"""
        self.total_steps = total_steps
        self.current_step = 0  # Сброс при установке нового total

    def update(self, current_internal_step, message):
        """
        Обновляет прогресс-бар и лог.
        current_internal_step: текущий шаг внутри программы (0 до total_steps-1)
        message: сообщение для отображения
        """
        self.current_step = current_internal_step
        # Рассчитываем общий процент выполнения:
        # Начало сегмента + (прогресс внутри программы / общее количество шагов внутри программы) * размер сегмента
        if self.total_steps > 0:
            internal_progress_ratio = self.current_step / self.total_steps
        else:
            internal_progress_ratio = 0  # Или 1, если шагов нет

        overall_progress_percent = self.segment_start_percent + (internal_progress_ratio * self.segment_size_percent)

        # Убеждаемся, что процент не превышает пределы сегмента
        overall_progress_percent = max(self.segment_start_percent,
                                       min(overall_progress_percent,
                                           self.segment_start_percent + self.segment_size_percent))

        # Округляем до целого для отображения
        overall_progress_percent = int(overall_progress_percent)

        self.gui_app.update_progress(overall_progress_percent, message)
        self.gui_app.log_message(message)


def main():
    root = tk.Tk()
    app = MainCNCprogrammeGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
