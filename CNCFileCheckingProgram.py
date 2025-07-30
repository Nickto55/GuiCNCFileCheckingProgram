import os
from itertools import count
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill
from openpyxl.worksheet.filters import FilterColumn, Filters
import openpyxl
import webbrowser
from datetime import date

listSpli = []
Recursion_Depth = 2
today = date.today()


def auto_fit_columns(sheet):
    for column_cells in sheet.columns:
        max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
        adjusted_width = (max_length - 20)  # Немного увеличим для красоты
        sheet.column_dimensions[get_column_letter(column_cells[0].column)].width = adjusted_width
    sheet.column_dimensions['A'].width = 5


def collect_subdirectories(root_dir_list: list, progress_tracker=None):
    global Recursion_Depth, today
    result = {}

    # Устанавливаем общее количество шагов для прогресса
    if progress_tracker:
        progress_tracker.set_total(len(root_dir_list))

    count = 0

    for dir_name in root_dir_list:
        # Обновляем прогресс
        if progress_tracker:
            progress_tracker.update(count, f"Обработка директории: {os.path.basename(dir_name)}")

        project_path = dir_name
        print(f"Создание листа: {os.path.basename(dir_name)}...")

        subdirs = []

        def recurse(path):
            global Recursion_Depth
            try:
                for item in os.listdir(path):
                    full_path = os.path.join(path, item)
                    if os.path.isdir(full_path):
                        if full_path.count("\\") == Recursion_Depth:
                            subdirs.append({'name': item, 'content': "", 'full_path': full_path})
                        recurse(full_path)
                    if full_path.count("\\") == Recursion_Depth + 1:
                        parent_dir = os.path.basename(os.path.dirname(full_path))
                        subdirs.append({'name': parent_dir, 'content': item, 'full_path': full_path})

            except PermissionError:
                print(f"Не удалось получить доступ к {path}")

        recurse(project_path)

        result[os.path.basename(dir_name)] = subdirs
        count += 1

    # Завершаем прогресс
    if progress_tracker:
        progress_tracker.update(len(root_dir_list), "Обработка директорий завершена")

    return result


def save_to_excel(data, output_file):
    column_indices = [1, 2, 3]
    data_range = "B1:E10"

    fill_color = PatternFill(start_color="d9d9d9", end_color="d9d9d9", fill_type="solid")

    wb = openpyxl.Workbook()
    del wb["Sheet"]

    for project_name, dirs in data.items():
        ws = wb.create_sheet(title=project_name[:31])

        # Заголовки
        headers = ["", "Название ДСЕ", "Содержимое", "Путь"]
        for col_num, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_num, value=header)

        # создание фильтра и его настройка
        ws.auto_filter.ref = data_range
        for col_index in column_indices:
            filter_column = FilterColumn(colId=col_index - 1)  # индексы в OpenPyXL начинаются с 0
            filters = Filters()
            filter_column.filters = filters
            ws.auto_filter.filterColumn.append(filter_column)

        for entry in dirs:
            if 'content' not in entry:
                entry['content'] = ""

        # данные
        for row_idx, entry in enumerate(dirs, 2):
            ws.cell(row=row_idx, column=2, value=entry['name'])

            # Расскраска
            cell = ws.cell(row=row_idx, column=3, value=entry['content'])
            if cell.value == "":
                for col_num in range(1, ws.max_column + 1):
                    cell = ws.cell(row=row_idx, column=col_num)
                    cell.fill = fill_color

            # Создание гиперссылки
            cell = ws.cell(row=row_idx, column=4, value=entry['full_path'])
            cell.hyperlink = f"{cell.value}"

        # Регулировка ширины столбцов
        auto_fit_columns(ws)
        ws.column_dimensions['A'].width = 5

        # Закрепление первой строки
        ws.freeze_panes = 'A2'

    wb.save(output_file)


def mainCNCFileCheckingProgram(list_main_repo: list, choseUser: int, twoProgramm: int, progress_tracker=None):
    global listSpli
    global Recursion_Depth

    # Получаем текущую директорию, где находится скрипт
    current_directory = os.getcwd()
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".CNCFileCheckingProgram")

    def nameUserSee(CONFIG_DIR):
        global nameUser
        nameUser = ""
        count = 0

        for i in CONFIG_DIR:
            if i == "\\":
                if count < 3:
                    count += 1
                else:
                    break
            if count == 2 and i != "\\":
                nameUser += i

    nameUserSee(CONFIG_DIR)

    if not list_main_repo:
        print(f"Не указано ни одного репозитория.")
        return

    main_repo = list_main_repo[0]

    Recursion_Depth = 2

    if not os.path.isdir(main_repo):
        print(f"Ошибка: '{main_repo}' не является допустимой директорией.")
        return

    # Передаем progress_tracker в collect_subdirectories
    data = collect_subdirectories(list_main_repo, progress_tracker)
    if not data:
        print(f"Нет подходящих подкаталогов для сохранения.")
        return

    output_file = f"BD_CNCprog_{today}"
    if not output_file.endswith(".xlsx"):
        output_file += ".xlsx"

    full_output_path = os.path.join(current_directory, output_file)

    def saveTry(data, full_output_path):
        try:
            save_to_excel(data, full_output_path)

        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
            saveTry(data, full_output_path)

    saveTry(data, full_output_path)

    if twoProgramm:
        return output_file


if __name__ == "__main__":
    mainCNCFileCheckingProgram([], 0, 0)