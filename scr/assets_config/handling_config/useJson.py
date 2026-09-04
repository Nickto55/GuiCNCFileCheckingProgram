import json
import os
import webbrowser
from datetime import datetime

from static.config import config_programm


class Jsondir:
    """
    Конфиг для сохранения директорий
    """

    def __init__(self, user_or_code: int, name_file_db=None):

        self.CONFIG_DIR = os.path.join(os.path.expanduser("~"), os.path.join('configs', ".CNCDirCheckingProgram"))
        self.CONFIG_FILE_DIR = os.path.join(self.CONFIG_DIR, "directories.json")

        self.directories = self.load_directories()

        Jsondir.main_use_json(self, user_or_code)

    def create_config_dir(self):

        if not os.path.exists(self.CONFIG_DIR):
            os.makedirs(self.CONFIG_DIR)
            return 0
        return 1

    @staticmethod
    def load_directories():
        config_file_dir = os.path.join(
            os.path.join(os.path.expanduser("~"), os.path.join('configs', ".CNCDirCheckingProgram")),
            "directories.json")
        if not os.path.exists(config_file_dir):
            return {}
        with open(config_file_dir, 'r', encoding='utf-8') as f:
            try:

                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save_directories(self, data):
        # Сохраняем директории в файл
        self.CONFIG_FILE_DIR.replace("\\", "/")
        with open(self.CONFIG_FILE_DIR, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def get_directory_info():
        while True:
            path = input(f"Введите полный путь к директории: ").strip()
            if os.path.isdir(path):
                break
            else:
                print(f"Неверный путь. Убедитесь, что путь существует и это директория.")
        return os.path.basename(path), path

    @staticmethod
    def list_directories(directories, user_or_code):  # Выводит список сохранённых директорий
        if not user_or_code:
            if not directories:
                print(f"Список директорий пуст.")
                return ""

            result = [f"\nСохранённые директории:"]
            for idx, (name, path) in enumerate(directories.items(), 1):
                result.append(f"{idx}. {name}: {path}")
            result.append("")
            return result
        else:
            result = []
            for idx, (name, path) in enumerate(directories.items(), 1):
                path = path.replace("\\", "/")
                result.append(f"{path}")
            return result

    def delete_directory(self, directories):
        # Удаляет директорию по выбору пользователя
        if not directories:
            print(f"Нет записей для удаления.")
            return

        Jsondir.list_directories(directories, 0)

        try:
            choice = int(input(f"Введите номер директории, которую хотите удалить: "))
            items = list(directories.items())
            if 1 <= choice <= len(items):
                key_to_delete = items[choice - 1][0]
                del directories[key_to_delete]
                Jsondir.save_directories(self, directories)
                print(f"Директория успешно удалена.")
            else:
                print(f"Некорректный номер.")
        except ValueError:
            print(f"Пожалуйста, введите число.")

    def code(self):
        directories = self.load_directories()
        returnu = Jsondir.list_directories(directories, 1)
        return returnu

    def main_use_json(self, user_or_code: int):

        def user():
            while True:
                print(
                    f"Меню:\n1. Добавить директорию\n2. Показать список директорий\n3. Удалить директорию\n4. Вернуться в основную программу\n5. Открыть файл с сохранёнными репозиториями")
                choice = input(f"Выберите действие (1/2/3/4/5): ").strip()

                if choice == "1":
                    name, path = Jsondir.get_directory_info()
                    if name in self.directories:
                        print(f"Директория с таким названием уже существует.")
                    else:
                        self.directories[name] = path
                        Jsondir.save_directories(self, self.directories)
                        print(f"Директория успешно добавлена.")

                elif choice == "2":
                    for i in Jsondir.list_directories(self.directories, 0):
                        print(i)
                elif choice == "3":
                    Jsondir.delete_directory(self, self.directories)
                elif choice == "4":
                    print(f"Выход из программы.")
                    print()
                    print("Вы вернулись в основную программу.")
                    break
                elif choice == "5":
                    webbrowser.open(self.CONFIG_FILE_DIR)
                else:
                    print(f"Некорректный выбор. Попробуйте ещё раз:")

        Jsondir.create_config_dir(self)

        if not user_or_code:
            user()


class JsonSave:
    """Конфиг для сохранения дат ДСЕ по станкам.
    Имеет вид:
    {
        "Станок 1": {
            "ДСЕ 1": "Дата 1",
            "ДСЕ 2": "Дата 2"
        },
        "Станок 2":{
            "ДСЕ 1": "Дата 1",
            "ДСЕ 2": "Дата 2"
        }
    }
    """

    def __init__(self):
        self.CONFIG_DIR = os.path.join(os.path.expanduser("~"), os.path.join('configs', ".CNCDirCheckingProgram"))
        self.file_path = os.path.join(self.CONFIG_DIR, "SaveDataFile.json")
        self.data = {}

        self._ensure_file_exists()
        self.load()

    def save(self):
        """Сохраняет текущие данные в файл."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    def _ensure_file_exists(self):
        """Создаёт файл и структуру данных, если их нет."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)

    def load(self):
        """Загружает данные из файла."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print("JsonSave файл пуст")

    def set_json(self, file_path):
        """
        Обновляет self.data, устанавливая для каждой папки (ДСЕ) дату последнего изменения файла.
        :param file_path: полный путь к файлу
        """
        machine = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
        dse_name = os.path.basename(file_path)

        modification_time = os.path.getmtime(file_path)
        file_date = datetime.fromtimestamp(modification_time)

        date_str = file_date.strftime("%Y-%m-%d %H:%M:%S")

        if machine not in self.data:
            self.data[machine] = {}

        self.data[machine][dse_name] = date_str

        self.save()

    @staticmethod
    def get_date(file_path):
        """
        Функция для получения даты если она есть, если нет то возрващает None
        :param file_path: Полная ссылка на файл
        :return: Date/None
        """
        machine = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
        dse_name = os.path.basename(file_path)
        return [machine, dse_name]


class JsonConfig:
    """
    Конфиг для сохранения настроек пользователя
    """

    def __init__(self):
        self.CONFIG_DIR = os.path.join(os.path.expanduser("~"), os.path.join('configs', ".CNCDirCheckingProgram"))
        self.file_path = os.path.join(self.CONFIG_DIR, "Config_BdCncProgram.json")
        self.data = config_programm
        self._ensure_file_exists()
        self.load()

    def save(self):
        """Сохраняет текущие данные в файл."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    def return_file_path(self):
        return self.file_path

    def _ensure_file_exists(self):
        """Создаёт файл и структуру данных, если их нет."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)

    def load(self):
        """Загружает данные из файла."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.data = config_programm

    def save_data(self):
        """Сохраняет текущие данные в файл."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    # Set
    def set_name(self, name):
        self.data["Name Program"] = name
        self.save_data()

    def set_name_automatically_file(self, name):
        self.data["Name ouput automaticallyFile"] = name
        self.set_path_automatically_file(name)

    def set_path_automatically_file(self, file_name):
        """На вход имя файла"""
        self.data["Path for output automaticallyFile"] = os.getcwd() + file_name
        self.save_data()

    def set_gui(self, bool_gui_prog):
        self.data["Run with GUI"] = bool(bool_gui_prog)
        self.save_data()

    def set_automatically(self, boolautomatically_prog):
        self.data["Run automatically"] = bool(boolautomatically_prog)
        self.save_data()

    def set_daate_automatically(self):
        self.data["last time use automatically search"] = f"{datetime.now()}"
        self.save_data()

    # Get
    def get_name(self):
        return self.data.get("Name Program", "")

    def get_name_automatically_file(self):
        return self.data.get("Name ouput automaticallyFile", "")

    def get_path_automatically_file(self):
        return self.data.get("Path for output automaticallyFile", "")

    def get_gui(self):
        return self.data.get("Run with GUI", "")

    def get_automatically(self):
        return self.data.get("Run automatically", "")

    def get_lsat_date_automatically(self):
        return self.data.get("last time use automatically search", "")

# if __name__ == "__main__":
#     run = JsonConfig()
#     run.setDaateAutomatically()
#     # print(run.setName("CNCFielChekingProgram"))
#     # print(run.getName())
#     run2 = JsonSave()
#     print(run2.data)
