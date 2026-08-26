import json
import os
import webbrowser
from datetime import datetime

from  static.config import config_programm


class Jsondir:
    """
    Конфиг для сохранения директорий
    """
    directories: str

    def __init__(self, userOrCode: int):
        global directories
        self.CONFIG_DIR = os.path.join(os.path.expanduser("~"), os.path.join('configs',".CNCDirCheckingProgram"))
        self.CONFIG_FILE_DIR = os.path.join(self.CONFIG_DIR, "directories.json")

        directories = Jsondir.load_directories(self)

        Jsondir.mainUseJson(self, userOrCode)

    def create_config_dir(self):

        if not os.path.exists(self.CONFIG_DIR):
            os.makedirs(self.CONFIG_DIR)
            return 0
        return 1

    def load_directories(self):
        CONFIG_FILE_DIR = os.path.join(os.path.join(os.path.expanduser("~"),os.path.join('configs',".CNCDirCheckingProgram")),
                                       "directories.json")
        # Загружаем существующие директории из файла
        if not os.path.exists(CONFIG_FILE_DIR):
            return {}
        with open(CONFIG_FILE_DIR, 'r', encoding='utf-8') as f:
            try:

                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save_directories(self, data):
        # Сохраняем директории в файл
        self.CONFIG_FILE_DIR.replace("\\", "/")
        with open(self.CONFIG_FILE_DIR, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_directory_info(self):
        while True:
            path = input(f"Введите полный путь к директории: ").strip()
            if os.path.isdir(path):
                break
            else:
                print(f"Неверный путь. Убедитесь, что путь существует и это директория.")
        return os.path.basename(path), path

    def list_directories(self, directories, userOrCode):  # Выводит список сохранённых директорий
        if not userOrCode:
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

        Jsondir.list_directories(self, directories, 0)

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
        directories = Jsondir.load_directories(self)
        returnu = Jsondir.list_directories(self, directories, 1)
        return returnu

    def mainUseJson(self, userOrCode: int):
        def user():
            while True:
                print(
                    f"Меню:\n1. Добавить директорию\n2. Показать список директорий\n3. Удалить директорию\n4. Вернуться в основную программу\n5. Открыть файл с сохранёнными репозиториями")
                choice = input(f"Выберите действие (1/2/3/4/5): ").strip()

                if choice == "1":
                    name, path = Jsondir.get_directory_info(self)
                    if name in directories:
                        print(f"Директория с таким названием уже существует.")
                    else:
                        directories[name] = path
                        Jsondir.save_directories(self, directories)
                        print(f"Директория успешно добавлена.")

                elif choice == "2":
                    for i in Jsondir.list_directories(self, directories, 0):
                        print(i)
                elif choice == "3":
                    Jsondir.delete_directory(self, directories)
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

        if not userOrCode:
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
        self.CONFIG_DIR = os.path.join(os.path.expanduser("~"), os.path.join('configs',".CNCDirCheckingProgram"))
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

    def setJson(self, file_path):
        """
        Обновляет self.data, устанавливая для каждой папки (ДСЕ) дату последнего изменения файла.
        :param file_path: полный путь к файлу
        """
        # Получаем компоненты пути
        machine = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
        dse_name = os.path.basename(file_path)

        # Получаем дату изменения файла
        modification_time = os.path.getmtime(file_path)
        file_date = datetime.fromtimestamp(modification_time)

        # Форматируем дату как строку (чтобы можно было сохранить в JSON)
        # Можно использовать: "2025-04-05 14:30:00" или ISO: "2025-04-05T14:30:00"
        date_str = file_date.strftime("%Y-%m-%d %H:%M:%S")  # или file_date.isoformat()

        # Создаём структуру: self.data[станок][дсе] = дата
        if machine not in self.data:
            self.data[machine] = {}

        # Перезаписываем дату для этой папки (ДСЕ)
        # Если файлов несколько — сохранится дата от последнего (или можно сравнивать, см. ниже)
        self.data[machine][dse_name] = date_str

        # Сохраняем состояние
        self.save()

    def getDate(self, file_path):
        """
        Функция для получения даты если она есть, если нет то возрващает None
        :param file_path: Полная ссылка на файл
        :return: Date/None
        """
        machine = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
        dse_name = os.path.basename(file_path)
        print(machine,"|",dse_name)


class JsonConfig:
    """
    Конфиг для сохранения настроек пользователя
    """

    def __init__(self):
        self.CONFIG_DIR = os.path.join(os.path.expanduser("~"), os.path.join('configs',".CNCDirCheckingProgram"))
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

    def save(self):
        """Сохраняет текущие данные в файл."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    # Set
    def setName(self, name):
        self.data["Name Program"] = name
        self.save()

    def setNameAutomaticallyFile(self, name):
        self.data["Name ouput automaticallyFile"] = name
        self.setPathAutomaticallyFile(name)

    def setPathAutomaticallyFile(self, file_name):
        """На вход имя файла"""
        self.data["Path for output automaticallyFile"] = os.getcwd() + file_name
        self.save()

    def setGui(self, boolGuiProg):
        self.data["Run with GUI"] = bool(boolGuiProg)
        self.save()

    def setAutomatically(self, boolautomaticallyProg):
        self.data["Run automatically"] = bool(boolautomaticallyProg)
        self.save()

    def setDaateAutomatically(self):
        self.data["last time use automatically search"] = f"{datetime.now()}"
        self.save()

    # Get
    def getName(self):
        return self.data.get("Name Program", "")

    def getNameAutomaticallyFile(self):
        return self.data.get("Name ouput automaticallyFile", "")

    def getPathAutomaticallyFile(self):
        return self.data.get("Path for output automaticallyFile", "")

    def getGui(self):
        return self.data.get("Run with GUI", "")

    def getAutomatically(self):
        return self.data.get("Run automatically", "")

    def getLsatDateAutomatically(self):
        return self.data.get("last time use automatically search", "")


# if __name__ == "__main__":
#     run = JsonConfig()
#     run.setDaateAutomatically()
#     # print(run.setName("CNCFielChekingProgram"))
#     # print(run.getName())
#     run2 = JsonSave()
#     print(run2.data)
