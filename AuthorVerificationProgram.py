import os
import tkinter as tk

import openpyxl
from openpyxl.styles import Alignment, PatternFill
from openpyxl.utils import get_column_letter


class ExcelPrint:
    def __init__(self, filename="results.xlsx", sheet_counterd: int = 0):
        self.filename = filename
        self.wb = openpyxl.Workbook()
        self.sheet_counter = sheet_counterd

    def sort_files_by_name(self, files_url1: list, files_url2: list):

        # Сортирует файлы по имени и объединяет строки с одинаковыми именами.
        # Возвращает два списка: для левой части (url1) и правой (url2).

        file_map = {}

        # Объединяем файлы по имени
        for file_info in files_url1:
            name = file_info["name"]
            if name not in file_map:
                file_map[name] = {"left": file_info, "right": None}
            else:
                file_map[name]["left"] = file_info  # можно оставить последнее или первое — зависит от задачи

        for file_info in files_url2:
            name = file_info["name"]
            if name not in file_map:
                file_map[name] = {"left": None, "right": file_info}
            else:
                file_map[name]["right"] = file_info

        # Создаем списки для левой и правой частей
        sorted_left = []
        sorted_right = []

        for name, pair in file_map.items():
            left_file = pair["left"]
            right_file = pair["right"]

            sorted_left.append(left_file or {"name": "", "url": "", "last_modified": ""})
            sorted_right.append(right_file or {"name": "", "url": "", "last_modified": ""})

        return sorted_left, sorted_right

    def auto_fit_columns(sheet):
        for column_cells in sheet.columns:
            max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
            adjusted_width = (max_length)  # Немного увеличим для красоты
            sheet.column_dimensions[get_column_letter(column_cells[0].column)].width = adjusted_width

    def add_sheet_for_number(self, sheeti, number: str, files_url1: list, files_url2: list, url1: str, url2: str,
                             sheet_counter=0):
        self.sheet_counter = sheet_counter

        fill_color = PatternFill(start_color="d9d9d9", end_color="d9d9d9", fill_type="solid")
        green_fill = PatternFill(start_color="0eec1d", end_color="0eec1d", fill_type="solid")
        yellow_fill = PatternFill(start_color="f4b706", end_color="f4b706", fill_type="solid")

        # Добавляет лист для указанного номера и записывает данные.
        sheet_name = f"{number[:30]}"  # Ограничение длины названия листа
        if sheet_name in self.wb.sheetnames:
            sheet_name += f"{self.sheet_counter}"
            self.sheet_counter += 1

        ws = self.wb.create_sheet(title=sheet_name)

        # Удаление начального листа "Sheet", если он ещё не удалён
        if "Sheet" in self.wb.sheetnames:
            del self.wb["Sheet"]

        # Ширина столбцов
        for col in range(1, 7):  # 6 столбцов
            ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 30

        # Первая строка: разделение на две части
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=2)
        ws.cell(row=1, column=1, value=os.path.basename(url1)).alignment = Alignment(horizontal="center")

        ws.merge_cells(start_row=1, start_column=6, end_row=1, end_column=7)
        ws.cell(row=1, column=6, value=os.path.basename(url2)).alignment = Alignment(horizontal="center")

        # Вторая строка: заголовки
        headers = [
            "Путь", "Дата изменения", "",
            "Имя файла", "", "Дата изменения", "Путь"
        ]
        for idx, header in enumerate(headers, start=1):
            cellU = ws.cell(row=2, column=idx, value=header)
            cellU.fill = fill_color

        # Сортировка и объединение
        sorted_left, sorted_right = self.sort_files_by_name(files_url1, files_url2)

        ws.column_dimensions['C'].fill = fill_color
        ws.column_dimensions['E'].fill = fill_color
        maxTimeFile = 0
        maxTimeFileList = [0, 0]

        # Заполнение данных
        for i in range(len(sorted_left)):
            row = i + 3  # начинаем с третьей строки

            left_file = sorted_left[i]
            right_file = sorted_right[i]

            # Левая часть (url1)
            ws.cell(row=row, column=1,
                    value=left_file["url"].replace(url1, "").lstrip("\\")).hyperlink = os.path.dirname(left_file["url"])
            cell_time_URL_1 = ws.cell(row=row, column=2, value=left_file["last_modified"])
            ws.cell(row=row, column=4, value=left_file["name"])

            # Правая часть (url2)
            cell_vale_name = ws.cell(row=row, column=4, value=right_file["name"])
            if cell_vale_name.value == "":
                ws.cell(row=row, column=4, value=left_file["name"])
            cell_time_URL_2 = ws.cell(row=row, column=6, value=right_file["last_modified"])
            ws.cell(row=row, column=7,
                    value=right_file["url"].replace(url2, "").lstrip("\\")).hyperlink = os.path.dirname(right_file[
                                                                                                            "url"])

            if cell_time_URL_1.value != "" and cell_time_URL_2.value != "":
                time_URL_1 = int(cell_time_URL_1.value.replace("-", "").replace(":", "").replace(" ", ""))
                time_URL_2 = int(cell_time_URL_2.value.replace("-", "").replace(":", "").replace(" ", ""))
                if time_URL_1 > time_URL_2:
                    ws.cell(row=row, column=3, value="").fill = green_fill
                    ws.cell(row=row, column=5, value="").fill = yellow_fill
                    if int(cell_time_URL_2.value.replace("-", "").replace(":", "").replace(" ", "")) > maxTimeFile:
                        maxTimeFile = int(cell_time_URL_2.value.replace("-", "").replace(":", "").replace(" ", ""))
                        maxTimeFileList = [row, 2]
                elif time_URL_1 < time_URL_2:
                    ws.cell(row=row, column=3, value="").fill = yellow_fill
                    ws.cell(row=row, column=5, value="").fill = green_fill
                    if int(cell_time_URL_1.value.replace("-", "").replace(":", "").replace(" ", "")) > maxTimeFile:
                        maxTimeFile = int(cell_time_URL_1.value.replace("-", "").replace(":", "").replace(" ", ""))
                        maxTimeFileList = [row, 6]
            elif cell_time_URL_1.value != "":
                if int(cell_time_URL_1.value.replace("-", "").replace(":", "").replace(" ", "")) > maxTimeFile:
                    maxTimeFile = int(cell_time_URL_1.value.replace("-", "").replace(":", "").replace(" ", ""))
                    maxTimeFileList = [row, 2]
            elif cell_time_URL_2.value != "":
                if int(cell_time_URL_2.value.replace("-", "").replace(":", "").replace(" ", "")) > maxTimeFile:
                    maxTimeFile = int(cell_time_URL_2.value.replace("-", "").replace(":", "").replace(" ", ""))
                    maxTimeFileList = [row, 6]
        if maxTimeFileList != [0,0]:
            ws.cell(row=maxTimeFileList[0], column=maxTimeFileList[1]).fill = green_fill
        print(number, maxTimeFileList)

        ExcelPrint.auto_fit_columns(ws)
        ws.column_dimensions['C'].width = 2
        ws.column_dimensions['E'].width = 2

    def save(self, output_text=None):
        """Сохраняет Excel-файл."""
        try:
            if output_text:
                output_text.insert(tk.END, f"\nФайл сохранён как {self.filename}\n")
            self.wb.save(self.filename)
        except Exception as e:
            print(f"Ошибка при сохранении Excel: {e}")
