import os
import json
import webbrowser


class jsonDir:
    directories: str

    def __init__(self, userOrCode: int):
        global directories
        self.CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".CNCDirCheckingProgram")
        self.CONFIG_FILE_DIR = os.path.join(self.CONFIG_DIR, "directories.json")

        directories = jsonDir.load_directories(self)

        jsonDir.mainUseJson(self, userOrCode)

    def create_config_dir(self):

        if not os.path.exists(self.CONFIG_DIR):
            os.makedirs(self.CONFIG_DIR)
            return 0
        return 1

    def load_directories(self):
        CONFIG_FILE_DIR = os.path.join(os.path.join(os.path.expanduser("~"), ".CNCDirCheckingProgram"), "directories.json")
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

        jsonDir.list_directories(self, directories, 0)

        try:
            choice = int(input(f"Введите номер директории, которую хотите удалить: "))
            items = list(directories.items())
            if 1 <= choice <= len(items):
                key_to_delete = items[choice - 1][0]
                del directories[key_to_delete]
                jsonDir.save_directories(self, directories)
                print(f"Директория успешно удалена.")
            else:
                print(f"Некорректный номер.")
        except ValueError:
            print(f"Пожалуйста, введите число.")

    def code(self):
        directories = jsonDir.load_directories(self)
        returnu = jsonDir.list_directories(self, directories, 1)
        return returnu

    def mainUseJson(self, userOrCode: int):
        def user():
            while True:
                print(
                    f"Меню:\n1. Добавить директорию\n2. Показать список директорий\n3. Удалить директорию\n4. Вернуться в основную программу\n5. Открыть файл с сохранёнными репозиториями")
                choice = input(f"Выберите действие (1/2/3/4/5): ").strip()

                if choice == "1":
                    name, path = jsonDir.get_directory_info(self)
                    if name in directories:
                        print(f"Директория с таким названием уже существует.")
                    else:
                        directories[name] = path
                        jsonDir.save_directories(self, directories)
                        print(f"Директория успешно добавлена.")

                elif choice == "2":
                    for i in jsonDir.list_directories(self, directories, 0):
                        print(i)
                elif choice == "3":
                    jsonDir.delete_directory(self, directories)
                elif choice == "4":
                    print(f"Выход из программы.")
                    print()
                    print("Вы вернулись в основную программу.")
                    break
                elif choice == "5":
                    webbrowser.open(self.CONFIG_FILE_DIR)
                else:
                    print(f"Некорректный выбор. Попробуйте ещё раз:")

        jsonDir.create_config_dir(self)

        if not userOrCode:
            user()


class jsonConfig():
    def __init__(self, CONFIG_DIR, Config_BdCncProgram):
        self.CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".CNCDirCheckingProgram")
        self.Config_BdCncProgram = os.path.join(CONFIG_DIR, "Config_BdCncProgram")

    def saveConfig_BdCncProgram(self, data):
        with open(self.Config_BdCncProgram, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    jsonDir(0)


