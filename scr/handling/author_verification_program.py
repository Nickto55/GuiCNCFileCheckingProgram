import os
from datetime import datetime

import openpyxl

SEARCH_COLUMN_TITLE = "Содержимое"
PATH_COLUMN_TITLE = "Путь"
RESULT_COLUMN_TITLE = "Автор"
DATA_COLUMN_TITLE = "Дата последнего изменения"
KB_COLUMN_TITLE = "KБ"
FILE_EXTENSIONS = [".nc", ".NC", ".h", ".H"]
SEARCH_FRAGMENT = "AVTOR"
IGNORED_SHEET = "ДСЕ по станкам"


def get_directory_size(directory_path: str) -> int:
    """
    Возвращает суммарный размер всех файлов в папке (включая вложенные папки) в байтах.

    Args:
        directory_path (str): Путь к папке.

    Returns:
        int: Размер папки в байтах.
    """
    total_size = 0

    try:
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except OSError:
                    pass
    except OSError as e:
        print(f"Ошибка при получении размера папки: {e}")
        raise

    return total_size


def main(excel_file, db_handler=None, progress_tracker=None):
    """
    Основная функция для поиска авторов в файлах и записи их в Excel.

    Args:
        excel_file (str): Путь к Excel-файлу для обработки.
        db_handler: Объект, у которого есть метод filling_database(data).
                    Обычно это self того класса, где находится ваш метод
                    filling_database.
        progress_tracker: Объект для отслеживания прогресса.
    """

    try:
        # Открываем Excel-файл
        wb = openpyxl.load_workbook(excel_file)
        sheets_to_process = [sheet for sheet in wb.sheetnames if sheet != IGNORED_SHEET]

        # Словарь для накопления данных под вашу функцию filling_database
        # Структура:
        # {
        #     "Имя листа/станка": [
        #         {"name": ..., "content": ..., "full_path": ...},
        #         ...
        #     ]
        # }
        data_for_db = {}

        total_steps = 0

        if progress_tracker:
            for sheet_name in sheets_to_process:
                ws = wb[sheet_name]
                estimated_rows = ws.max_row - 1 if ws.max_row > 1 else 0
                total_steps += max(estimated_rows, 0)

            progress_tracker.set_total(total_steps)

        current_step = 0

        for sheet_name in sheets_to_process:
            ws = wb[sheet_name]

            # Имя листа используем как name_machine_directory
            data_for_db[sheet_name] = []

            # Получаем заголовки первого ряда
            try:
                headers = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
            except StopIteration:
                headers = ()

            content_col, path_col, result_col, data_col, kb_col = None, None, None, None, None

            for idx, header in enumerate(headers):
                if header == SEARCH_COLUMN_TITLE:
                    content_col = idx + 1
                elif header == PATH_COLUMN_TITLE:
                    path_col = idx + 1
                elif header == DATA_COLUMN_TITLE:
                    data_col = idx + 1
                elif header == KB_COLUMN_TITLE:
                    kb_col = idx + 1
                elif header == RESULT_COLUMN_TITLE:
                    result_col = idx + 1

            # Если заголовок результата не найден — добавляем его
            if result_col is None:
                result_col = len(headers) + 1
                ws.cell(row=1, column=result_col, value=RESULT_COLUMN_TITLE)

            # Если заголовок даты не найден — добавляем его
            if data_col is None:
                data_col = len(headers) + 1
                ws.cell(row=1, column=data_col, value=DATA_COLUMN_TITLE)

            # Если заголовок размера в КБ не найден — добавляем его
            if kb_col is None:
                kb_col = len(headers) + 1
                ws.cell(row=1, column=kb_col, value=KB_COLUMN_TITLE)

            # Проверяем, что найдены все нужные столбцы
            if not all([content_col, path_col]):
                print(
                    f"Столбцы '{SEARCH_COLUMN_TITLE}' или '{PATH_COLUMN_TITLE}' "
                    f"не найдены на листе '{sheet_name}'"
                )

                if progress_tracker:
                    estimated_rows = ws.max_row - 1 if ws.max_row > 1 else 0
                    for _ in range(estimated_rows):
                        progress_tracker.update(
                            current_step,
                            f"Пропущен лист '{sheet_name}' (нет столбцов)"
                        )
                        current_step += 1

                continue

            # Обрабатываем каждую строку
            rows_data = list(ws.iter_rows(min_row=2, values_only=False))

            for row_idx, row in enumerate(rows_data, start=2):
                file_name_cell = row[content_col - 1]
                path_cell = row[path_col - 1]

                progress_message = (
                    f"Обработка листа '{sheet_name}', "
                    f"строка {row_idx - 1}/{len(rows_data)}"
                )

                if not (file_name_cell.value and path_cell.value):
                    if progress_tracker:
                        progress_tracker.update(
                            current_step,
                            progress_message + " - Пропущена (пустая)"
                        )
                        current_step += 1

                    if kb_col:
                        row[kb_col - 1].value = ""
                    if data_col:
                        row[data_col - 1].value = ""
                    if result_col:
                        row[result_col - 1].value = ""

                    continue

                file_name = str(file_name_cell.value).strip()
                full_path = str(path_cell.value).strip()

                # Проверяем расширение файла
                if not any(file_name.endswith(ext) for ext in FILE_EXTENSIONS):
                    if progress_tracker:
                        progress_tracker.update(
                            current_step,
                            progress_message + " - Пропущена (расширение)"
                        )
                        current_step += 1

                    if kb_col:
                        row[kb_col - 1].value = ""
                    if data_col:
                        row[data_col - 1].value = ""

                    continue

                # Проверяем существование файла
                if not os.path.exists(full_path):
                    if progress_tracker:
                        progress_tracker.update(
                            current_step,
                            progress_message + " - Ошибка (файл не найден)"
                        )
                        current_step += 1

                    if kb_col:
                        row[kb_col - 1].value = "Файл не найден"
                    if data_col:
                        row[data_col - 1].value = "Файл не найден"
                    if result_col:
                        row[result_col - 1].value = "Файл не найден"

                    continue

                try:
                    # Получаем размер файла или директории
                    if os.path.isfile(full_path):
                        size_bytes = os.path.getsize(full_path)
                    else:
                        size_bytes = get_directory_size(full_path)

                    size_kb = round(size_bytes / 1024)

                    if kb_col:
                        row[kb_col - 1].value = size_kb

                    # Получаем дату последнего изменения
                    mod_time = os.path.getmtime(full_path)
                    mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')

                    if data_col:
                        row[data_col - 1].value = mod_date

                    # Читаем содержимое файла и ищем автора
                    file_content = ""
                    avtor_value = "Не найден"

                    if os.path.isfile(full_path):
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            file_content = f.read()

                        for line in file_content.splitlines():
                            if SEARCH_FRAGMENT in line:
                                avtor_line = line.strip()
                                avtor_parts = avtor_line.split("AVTOR:", 1)

                                if len(avtor_parts) > 1:
                                    avtor_value = avtor_parts[1].strip()

                                    if avtor_value.startswith('(') and avtor_value.endswith(')'):
                                        avtor_value = avtor_value[1:-1]
                                    else:
                                        if avtor_value.startswith('('):
                                            avtor_value = avtor_value[1:]
                                        if avtor_value.endswith(')'):
                                            avtor_value = avtor_value[:-1]

                                    avtor_value = avtor_value.strip()

                                break

                    if result_col:
                        row[result_col - 1].value = avtor_value

                    # Накапливаем данные для вашей функции filling_database.
                    # Проверка нужна, потому что внутри filling_database используется:
                    # link.index(name_machine_directory)
                    # link.index(dse_name)
                    # Если этих подстрок не будет, функция упадет с ValueError.
                    if (
                        os.path.isfile(full_path)
                        and sheet_name in full_path
                        and full_path.endswith(file_name)
                    ):
                        data_for_db[sheet_name].append(
                            {
                                "name": file_name,
                                "content": file_content,
                                "full_path": full_path,
                            }
                        )

                    if progress_tracker:
                        progress_tracker.update(
                            current_step,
                            progress_message + " - Обработан"
                        )
                        current_step += 1

                except Exception as e:
                    if progress_tracker:
                        progress_tracker.update(
                            current_step,
                            progress_message + f" - Ошибка ({type(e).__name__})"
                        )
                        current_step += 1

                    if kb_col:
                        row[kb_col - 1].value = f"Ошибка: {e}"
                    if data_col:
                        row[data_col - 1].value = f"Ошибка: {e}"
                    if result_col:
                        row[result_col - 1].value = f"Ошибка: {e}"

        # Сначала сохраняем Excel, чтобы не потерять результаты,
        # если вдруг база данных упадет с ошибкой.
        wb.save(excel_file)
        print("Обработка завершена. Результаты записаны в исходный файл.")

        # Вызов вашей функции заполнения базы данных
        if db_handler is not None:
            try:
                db_handler.filling_database(data_for_db)
                print("База данных заполнена.")
            except Exception as db_error:
                print(f"Ошибка при заполнении базы данных: {db_error}")
                raise
        else:
            print("db_handler не передан, запись в базу данных пропущена.")

        if progress_tracker and current_step < total_steps:
            for i in range(current_step, total_steps):
                progress_tracker.update(i, "Завершение...")

            if total_steps > 0:
                progress_tracker.update(total_steps - 1, "Обработка авторов завершена")

    except Exception as e:
        print(f"Критическая ошибка в main AuthorVerificationProgram: {e}")
        raise