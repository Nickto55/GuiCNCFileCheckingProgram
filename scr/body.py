import os
import sys
import json
import time
import plyer
import threading
import webbrowser
import tkinter as tk

from tkinter import *
from datetime import date
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, messagebox, filedialog

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )
)

from scr.assets_config.handling_config.useJson import JsonConfig
from scr.cnc_file_checking_program import run_program, today


def seconds_to_minutes_seconds(seconds):
    """
    Преобразует секунды в минуты и секунды.
    """
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return minutes, remaining_seconds


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("..")

    return os.path.join(base_path, relative_path)


change_dir_cb_bool = 0


class GuiDirManager:
    """
    GUI версия менеджера директорий.
    """

    def __init__(self, parent):
        self.parent = parent
        self.directories = {}

        self.CONFIG_DIR = os.path.join(
            os.path.expanduser("~"),
            ".CNCDirCheckingProgram"
        )

        self.CONFIG_FILE_DIR = os.path.join(
            self.CONFIG_DIR,
            "directories.json"
        )

        self.create_config_dir()
        self.load_directories()

    def return_name_file(self):
        return self.CONFIG_FILE_DIR

    def create_config_dir(self):
        if not os.path.exists(self.CONFIG_DIR):
            os.makedirs(self.CONFIG_DIR)

    def load_directories(self):
        if not os.path.exists(self.CONFIG_FILE_DIR):
            self.directories = {}
            return

        try:
            with open(self.CONFIG_FILE_DIR, "r", encoding="utf-8") as f:
                self.directories = json.load(f)
        except Exception:
            self.directories = {}

    def save_directories(self):
        try:
            with open(self.CONFIG_FILE_DIR, "w", encoding="utf-8") as f:
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


class WindowFileNameManager:
    """
    Окно управления выходным файлом.
    """

    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Управление выходным файлом")
        self.window.geometry("600x620")
        self.window.resizable(False, False)

        try:
            icon_path = resource_path("../static/img/ico/gear.ico")
            self.window.iconbitmap(icon_path)
        except Exception as e:
            print(f"Не удалось установить иконку: {e}")

    def returnRoot(self):
        return self.window


class WindowDirectoryManager:
    """
    Окно управления директориями.
    """

    def __init__(self, parent, dir_manager):
        self.window = tk.Toplevel(parent)
        self.window.title("Управление директориями")
        self.window.geometry("600x400")
        self.window.resizable(False, False)

        try:
            icon_path = resource_path("../static/img/ico/dirBook.ico")
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

        browse_btn = ttk.Button(
            add_frame,
            text="Обзор",
            command=self.browse_directory
        )
        browse_btn.grid(row=0, column=4, padx=(0, 5))

        add_btn = ttk.Button(
            add_frame,
            text="Добавить",
            command=self.add_directory
        )
        add_btn.grid(row=0, column=5)

        # Фрейм для списка директорий
        list_frame = ttk.LabelFrame(self.window, text="Сохранённые директории", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("name", "path"),
            show="headings",
            height=10
        )

        self.tree.heading("name", text="Имя")
        self.tree.heading("path", text="Путь")

        self.tree.column("name", width=150)
        self.tree.column("path", width=400)

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", padx=10, pady=5)

        delete_btn = ttk.Button(
            button_frame,
            text="Удалить",
            command=self.delete_directory
        )
        delete_btn.pack(side="left", padx=(0, 5))

        open_file_btn = ttk.Button(
            button_frame,
            text="Открыть файл с директориями",
            command=self.open_config_file
        )
        open_file_btn.pack(side="left", padx=(0, 5))

        close_btn = ttk.Button(
            button_frame,
            text="Закрыть",
            command=self.window.destroy
        )
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
            messagebox.showerror(
                "Ошибка",
                "Указанный путь не существует или не является директорией"
            )
            return

        if not name or not path:
            messagebox.showwarning(
                "Предупреждение",
                "Пожалуйста, заполните все поля"
            )
            return

        if self.dir_manager.add_directory(name, path):
            self.name_entry.delete(0, tk.END)
            self.path_entry.delete(0, tk.END)

            self.refresh_list()

            messagebox.showinfo(
                "Успех",
                "Директория успешно добавлена"
            )
        else:
            messagebox.showerror(
                "Ошибка",
                "Директория с таким именем уже существует"
            )

    def delete_directory(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Предупреждение",
                "Пожалуйста, выберите директорию для удаления"
            )
            return

        index = self.tree.index(selected[0])

        if self.dir_manager.delete_directory(index):
            self.refresh_list()

            messagebox.showinfo(
                "Успех",
                "Директория успешно удалена"
            )
        else:
            messagebox.showerror(
                "Ошибка",
                "Не удалось удалить директорию"
            )

    def open_config_file(self):
        self.dir_manager.open_config_file()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for name, path in self.dir_manager.directories.items():
            self.tree.insert(
                "",
                "end",
                values=(name, path)
            )


def send_notification(title, message, settime=15, file_path=""):
    try:
        plyer.notification.notify(
            title=title,
            message=message,
            app_name="ToolCheckerProgram",
            timeout=settime
        )
    except Exception as e:
        print(f"Не удалось показать уведомление: {e}")

    if file_path and os.path.exists(file_path):
        try:
            os.startfile(file_path)
        except Exception as e:
            print(f"Не удалось открыть файл из уведомления: {e}")


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

        try:
            icon_path = resource_path("../static/img/ico/iconca.ico")
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Не удалось установить иконку: {e}")

        self.dir_manager = GuiDirManager(self.root)

        self.log_frame_Bool = 0

        self.timerWorkProg = StringVar(value="Время работы программы: Нет")
        self.timerWorkProgBool = 1

        self.run_cnc_checking = tk.BooleanVar()
        self.run_data_checker = tk.BooleanVar()
        self.run_author_verification = tk.BooleanVar()

        self.choseUserChangeDir = tk.BooleanVar()
        self.choseUserUseSaveDir = tk.BooleanVar(value=True)

        self.custom_output_file = tk.StringVar()

        self.config_json = JsonConfig()

        self.file_window = None

        main_menu = tk.Menu(self.root)

        settings_menu = tk.Menu(main_menu, tearoff=0)
        settings_menu.add_command(
            label="Отобразить ход программы",
            command=self.log_frame_command
        )
        settings_menu.add_command(
            label="Имя файла",
            command=self.file_frame_command
        )
        settings_menu.add_command(
            label="Run config json",
            command=self.run_config_file_json
        )
        settings_menu.add_command(
            label="Графический интерфейс",
            command=self.selection_gui_command
        )

        main_menu.add_cascade(label="Settings", menu=settings_menu)
        main_menu.add_cascade(
            label="Saved Directories",
            command=self.open_directory_manager
        )
        main_menu.add_cascade(
            label="Help",
            command=lambda: self.show_program_info(self.root)
        )

        self.root.config(menu=main_menu)

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
        Отображает информацию о программе.
        """
        info_window = tk.Toplevel(parent)
        info_window.title("Информация о программе")
        info_window.geometry("600x1250")
        info_window.resizable(False, False)
        info_window.overrideredirect(True)

        try:
            icon_path = resource_path("../static/img/ico/gear.ico")
            info_window.iconbitmap(icon_path)
        except Exception as e:
            print(f"Не удалось установить иконку: {e}")

        if parent:
            parent_x = parent.winfo_x()
            parent_y = parent.winfo_y()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()

            x = parent_x + (parent_width // 2) - (600 // 2)
            y = parent_y + (parent_height // 2) - (500 // 2)

            if x < 0 or y < 0:
                info_window.geometry("600x500")
            else:
                info_window.geometry(f"600x500+{x}+{y}")

        info_window.lift()
        info_window.focus_force()

        main_frame = ttk.Frame(info_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_frame.bind(
            "<B1-Motion>",
            lambda e: info_window.geometry("+{0}+{1}".format(e.x_root, e.y_root))
        )

        title_label = ttk.Label(
            main_frame,
            text="GuiCNCFileCheckingProgram",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        description_text = (
            "Версия программы CNCFileCheckingProgram с графическим интерфейсом "
            "и ограниченным функционалом"
        )

        description_label = ttk.Label(
            main_frame,
            text=description_text,
            wraplength=550,
            justify=tk.LEFT
        )
        description_label.pack(pady=(0, 15))

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        components_frame = ttk.Frame(notebook)
        notebook.add(components_frame, text="Основные компоненты")

        components_text = """
• Программа обработки директорий - Основа CNCFileCheckingProgram. Формирует Excel-таблицу с информацией о директориях, содержащих ДСЕ, их содержимом и прямыми ссылками на файлы.

• Программа создания сводной таблицы - Создаёт лист «ДСЕ по станкам», в котором отображаются данные о ДСЕ и станках, на которых они используются. Также указывается дата последнего изменения файла.

• Программа отображения авторов NC- и H-файлов - Позволяет просматривать информацию об авторах NC- и H-файлов.
"""

        components_text_widget = ScrolledText(
            components_frame,
            wrap=tk.WORD,
            width=60,
            height=15,
            font=("Arial", 10)
        )

        components_text_widget.pack(
            fill=tk.BOTH,
            expand=True,
            padx=5,
            pady=5
        )

        components_text_widget.insert(tk.END, components_text)
        components_text_widget.config(state=tk.DISABLED)

        menu_frame = ttk.Frame(notebook)
        notebook.add(menu_frame, text="Меню")

        menu_tree = ttk.Treeview(
            menu_frame,
            columns=("Описание",),
            show="tree headings",
            height=15
        )

        menu_tree.heading("#0", text="Пункт меню")
        menu_tree.heading("Описание", text="Описание")

        menu_tree.column("#0", width=150)
        menu_tree.column("Описание", width=350)

        settings = menu_tree.insert(
            "",
            "end",
            text="1. Settings",
            open=True
        )

        menu_tree.insert(
            settings,
            "end",
            text="1. Отображать ход выполнения",
            values=("Включает вывод логов и процесса выполнения программы",)
        )

        menu_tree.insert(
            settings,
            "end",
            text="2. Имя файла",
            values=("Позволяет просмотреть или задать имя исполняемого файла",)
        )

        menu_tree.insert(
            settings,
            "end",
            text="3. Run config json",
            values=("Открывает конфигурационный JSON-файл с указанием директорий",)
        )

        saved_dirs = menu_tree.insert(
            "",
            "end",
            text="2. Saved Directories",
            values=("Просмотр и настройка списка сохранённых директорий",)
        )

        menu_tree.insert(
            "",
            "end",
            text="3. Help",
            values=("help",)
        )

        menu_tree.pack(
            fill=tk.BOTH,
            expand=True,
            padx=5,
            pady=5
        )

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        close_button = ttk.Button(
            button_frame,
            text="Закрыть",
            command=info_window.destroy
        )
        close_button.pack(side=tk.RIGHT)

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
            self.log_frame.place(
                x=10,
                y=distanceY,
                height=650 - distanceY,
                width=680
            )

        self.log_frame_Bool = not self.log_frame_Bool

    def open_directory_manager(self):
        WindowDirectoryManager(self.root, self.dir_manager)

    def browse_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ],
            title="Выберите файл для сохранения"
        )

        if filename:
            self.custom_output_file.set(filename)

    def log_message(self, message):
        if not hasattr(self, "log_text"):
            return

        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

        self.root.update_idletasks()

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def start_program(self):
        mode = self.operating_mode_var.get()

        print(mode)

        if mode == "0":
            messagebox.showwarning(
                "Внимание",
                "Перед началом выберете режим работы!"
            )
            return

        elif mode == "2":
            self.file_frame_command()

            if self.timerWorkProgBool:
                self.timer_label.place_forget()
                self.timerWorkProgBool = not self.timerWorkProgBool

            self.progress.place(x=5, y=self.maxDistanceY - 5)
            self.progress_label.grid()

            if not any([
                self.run_cnc_checking.get(),
                self.run_data_checker.get(),
                self.run_author_verification.get()
            ]):
                self.progress.place_forget()
                self.progress_label.grid_remove()

                messagebox.showwarning(
                    "Предупреждение",
                    "Пожалуйста, выберите хотя бы одну программу для запуска"
                )
                return

            self.progress["value"] = 0
            self.progress_label.config(text="Подготовка...")

            directories = self.dir_manager.get_directories_list()
            output_file = self.get_output_filename()

            run_cnc = self.run_cnc_checking.get()
            run_data = self.run_data_checker.get()
            run_author = self.run_author_verification.get()

            def progress_callback(percent, text):
                self.root.after(
                    0,
                    self.update_progress,
                    percent,
                    text
                )

            def log_callback(message):
                self.root.after(
                    0,
                    self.log_message,
                    message
                )

            def worker():
                try:
                    result = run_program(
                        run_cnc=run_cnc,
                        run_data=run_data,
                        run_author=run_author,
                        output_file=output_file,
                        directories=directories,
                        log_callback=log_callback,
                        progress_callback=progress_callback
                    )

                    self.root.after(
                        0,
                        self.on_program_success,
                        result
                    )

                except Exception as e:
                    self.root.after(
                        0,
                        self.on_program_error,
                        str(e)
                    )

            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()

        else:
            messagebox.showerror(
                "Ошибка",
                "Что то пошло не так при выборе режима работы"
            )

    def on_program_success(self, result):
        result = result or {}

        self.progress["value"] = 100
        self.progress_label.config(text="Завершено!")

        self.progress.place_forget()
        self.progress_label.grid_remove()

        execution_time = result.get("execution_time", 0)

        try:
            execution_time = int(execution_time)
        except Exception:
            execution_time = 0

        minutes, seconds = seconds_to_minutes_seconds(execution_time)

        self.timerWorkProgBool = 1
        self.timerWorkProg.set(
            f"Время работы программы: {minutes}мин {seconds}сек"
        )

        self.timer_label.place(
            x=5,
            y=self.maxDistanceY,
            height=24
        )

        file_to_open = result.get("file_to_open", "")

        self.ask_open_file(file_to_open)

        if file_to_open and os.path.exists(file_to_open):
            notification_file_name = os.path.basename(file_to_open)
        else:
            notification_file_name = self.get_output_filename()

        send_notification(
            "Программа завершена.",
            f"Программа ToolCheckerProgram завершена, данные сохранены в файл: {notification_file_name}",
            15
        )

        self.root.after(
            2000,
            lambda: self.update_progress(0, "Готово")
        )

    def on_program_error(self, error_msg):
        error_msg = f"Ошибка выполнения: {error_msg}"

        self.log_message(error_msg)

        self.progress.place_forget()
        self.progress_label.grid_remove()

        messagebox.showerror("Ошибка", error_msg)

        self.root.after(
            2000,
            lambda: self.update_progress(0, "Готово")
        )

    def update_progress(self, value, text):
        """
        Обновление прогресс-бара.
        """
        try:
            self.progress["value"] = float(value)
        except Exception:
            self.progress["value"] = 0

        self.progress_label.config(text=str(text))

        self.root.update_idletasks()

    def get_output_filename(self):
        output_file = self.custom_output_file.get().strip()

        if not output_file:
            output_file = f"BD_CNCprog_{date.today()}"

        if not output_file.lower().endswith(".xlsx"):
            output_file += ".xlsx"

        return output_file

    def create_widgets(self):
        global change_dir_cb_bool

        offsetX = 5
        offsetY = 0
        maxDistanceY = self.maxDistanceY
        distanseY = 25

        # Фрейм для выбора программ
        program_frame = ttk.LabelFrame(
            self.root,
            text="Выберите программы для запуска:",
            padding=10
        )
        program_frame.place(
            x=offsetX,
            y=offsetY,
            height=100,
            width=330
        )

        cnc_cb = ttk.Checkbutton(
            program_frame,
            text="Программа обработки директорий",
            variable=self.run_cnc_checking
        )
        cnc_cb.place(x=offsetX, y=0)

        data_cb = ttk.Checkbutton(
            program_frame,
            text="Программа создания сводной таблицы",
            variable=self.run_data_checker
        )
        data_cb.place(x=offsetX, y=offsetY + distanseY)

        author_cb = ttk.Checkbutton(
            program_frame,
            text="Программа отображения авторов nc и h файлов",
            variable=self.run_author_verification
        )
        author_cb.place(x=offsetX, y=offsetY + distanseY * 2)

        operating_mode = ttk.LabelFrame(
            self.root,
            text="Выберите режим работы:",
            padding=10
        )
        operating_mode.place(
            x=offsetX + 530,
            y=offsetY,
            height=100,
            width=160
        )

        operating_mode_chose = ttk.Radiobutton(
            operating_mode,
            text="Ничего",
            value="0",
            variable=self.operating_mode_var
        )
        operating_mode_chose.grid(row=0, column=0, sticky="w")

        operating_mode_automatically = ttk.Radiobutton(
            operating_mode,
            text="Только различные",
            value="1",
            variable=self.operating_mode_var
        )
        operating_mode_automatically.grid(row=1, column=0, sticky="w")

        operating_mode_full = ttk.Radiobutton(
            operating_mode,
            text="Всё",
            value="2",
            variable=self.operating_mode_var
        )
        operating_mode_full.grid(row=2, column=0, sticky="w")

        self.run_cnc_checking.set(True)
        self.run_data_checker.set(False)
        self.run_author_verification.set(False)

        # Фрейм для настроек директорий
        dir_frame = ttk.LabelFrame(
            self.root,
            text="Настройки директорий",
            padding=10
        )
        dir_frame.pack(fill="x", padx=10, pady=5)

        # Прогресс-бар
        progress_frame = ttk.Frame(self.root)
        progress_frame.place(
            x=offsetX,
            y=maxDistanceY,
            height=60
        )

        self.progress = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            length=600,
            maximum=100
        )
        self.progress.place(x=5, y=self.maxDistanceY - 5)

        self.progress_label = ttk.Label(
            progress_frame,
            text="Готово"
        )
        self.progress_label.grid(row=1, column=0)

        self.progress.place_forget()
        self.progress_label.grid_remove()

        self.timer_label = Label(
            self.root,
            textvariable=self.timerWorkProg
        )
        self.timer_label.place(
            x=5,
            y=self.maxDistanceY - 1,
            height=24
        )
        self.timer_label.place_forget()

        # Кнопка запуска
        run_btn = ttk.Button(
            self.root,
            text="Начать",
            command=self.start_program
        )
        run_btn.place(
            x=615,
            y=maxDistanceY - 1,
            height=24
        )

        # Текстовое поле для логов
        self.log_frame = ttk.LabelFrame(
            self.root,
            text="Лог выполнения",
            padding=5
        )
        self.log_frame.place(x=5, y=168)

        self.log_text = tk.Text(
            self.log_frame,
            height=12,
            wrap="word"
        )

        scrollbar = ttk.Scrollbar(
            self.log_frame,
            orient="vertical",
            command=self.log_text.yview
        )

        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(side="right", fill="y")

        clear_log_btn = ttk.Button(
            self.log_text,
            text="Очистить лог",
            command=self.clear_log
        )
        clear_log_btn.pack(pady=5, anchor="e")

        self.log_frame.place_forget()

        self.root.geometry(f"700x{self.distanceMinY}")

    def file_frame_command(self):
        """
        Открывает окно имени выходного файла.
        """
        if getattr(self, "file_window", None) is not None:
            try:
                if self.file_window.winfo_exists():
                    self.file_window.lift()
                    self.file_window.focus_force()
                    return
            except Exception:
                self.file_window = None

        classRoot = WindowFileNameManager(self.root)
        self.file_window = classRoot.returnRoot()

        def on_close():
            self.file_window = None
            classRoot.window.destroy()

        self.file_window.protocol("WM_DELETE_WINDOW", on_close)

        file_frame = ttk.LabelFrame(
            self.file_window,
            text="Имя выходного файла",
            padding=10
        )
        file_frame.pack(fill="x", padx=10, pady=5)

        self.output_file_entry = ttk.Entry(
            file_frame,
            textvariable=self.custom_output_file
        )
        self.output_file_entry.pack(
            fill="x",
            side="left",
            expand=True
        )

        output_file = f"BD_CNCprog_{date.today()}"

        if not output_file.endswith(".xlsx"):
            output_file += ".xlsx"

        self.output_file_entry.delete(0, END)
        self.output_file_entry.insert(0, output_file)

        browse_btn = ttk.Button(
            file_frame,
            text="Выбрать файл",
            command=self.browse_file
        )
        browse_btn.pack(side="right", padx=(5, 0))

    def ask_open_file(self, file_path):
        """
        Запрос на открытие файла в основном потоке.
        """
        if messagebox.askyesno(
            "Открыть файл",
            "Обработка завершена. Хотите открыть файл?"
        ):
            if file_path and os.path.exists(file_path):
                webbrowser.open(file_path)
            else:
                messagebox.showerror(
                    "Ошибка",
                    f"Файл не найден: {file_path}"
                )


if __name__ == "__main__":
    root = tk.Tk()
    app = MainCNCprogrammeGUI(root)
    root.mainloop()