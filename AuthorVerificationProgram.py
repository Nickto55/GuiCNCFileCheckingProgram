import openpyxl
import os

from CNCFileCheckingProgram import today
from Config import outputFileDef

# Параметры
def main(excel_file):
    search_column_title = "Содержимое"  # Заголовок столбца с именами файлов
    path_column_title = "Путь"  # Заголовок столбца с полными путями
    result_column_title = "Автор"  # Заголовок для нового столбца с результатами
    file_extensions = [".nc", ".NC", ".h", ".H"]  # Поддерживаемые расширения
    search_fragment = "AVTOR"  # Фрагмент строки для поиска
    ignored_sheet = "ДСЕ по станкам"  # Лист, который нужно пропустить

    # Открываем Excel-файл
    wb = openpyxl.load_workbook(excel_file)
    sheets_to_process = [sheet for sheet in wb.sheetnames if sheet != ignored_sheet]

    for sheet_name in sheets_to_process:
        ws = wb[sheet_name]
        print(f"Обработка листа: {sheet_name}")

        # Находим номера столбцов по заголовкам
        headers = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))  # Получаем первую строку (заголовки)
        content_col, path_col, result_col = None, None, None

        for idx, header in enumerate(headers):
            if header == search_column_title:
                content_col = idx + 1  # Индексы в OpenPyXL начинаются с 1
            elif header == path_column_title:
                path_col = idx + 1
            elif header == result_column_title:
                result_col = idx + 1  # Если столбец уже существует

        # Если заголовок результата не найден — добавляем его
        if result_col is None:
            result_col = len(headers) + 1
            ws.cell(row=1, column=result_col, value=result_column_title)

        # Проверяем, что найдены все нужные столбцы
        if not all([content_col, path_col]):
            print(f"Столбцы '{search_column_title}' или '{path_column_title}' не найдены на листе '{sheet_name}'")
            continue

        # Обрабатываем каждую строку
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):  # Начинаем со второй строки
            file_name_cell = row[content_col - 1]
            path_cell = row[path_col - 1]

            if not (file_name_cell.value and path_cell.value):
                continue  # Пропускаем пустые ячейки

            file_name = str(file_name_cell.value).strip()
            full_path = str(path_cell.value).strip()

            # Проверяем расширение файла
            if not any(file_name.endswith(ext) for ext in file_extensions):
                continue

            # Проверяем существование файла
            if not os.path.exists(full_path):
                print(f"Файл не существует: {full_path}")
                continue

            try:
                with open(full_path, 'r') as f:
                    for line in f:
                        if search_fragment in line:
                            avtor_line = line.strip()
                            avtor_value = avtor_line.replace("AVTOR:", "").strip()

                            # Записываем результат в столбец "Автор"
                            result_cell = row[result_col - 1]
                            if avtor_value.find("(") > -1: avtor_value = avtor_value[avtor_value.find("("):]
                            result_cell.value = avtor_value[2:][:-2]
                            break
            except Exception as e:
                print(f"Ошибка при открытии файла {full_path}: {e}")

    # Сохраняем изменения
    wb.save(excel_file)
    print("Обработка завершена. Результаты записаны в исходный файл.")

if __name__ == "__main__":
    output_file = f"BD_CNCprog_{today}"
    if not output_file.endswith(".xlsx"):
        output_file += ".xlsx"
    main(output_file)