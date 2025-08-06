import os

import colorama
from colorama import Fore
def dataHex(data):
    if data is not None:
        hex_string = ' '.join(f'{b:02X}' for b in data)
        return hex_string
    return None


def read_bytes_at_offset(file_path, start_offset = 0, end_offset = 1):
    """
    Читает байты из файла в заданном диапазоне смещений.

    Args:
        file_path (str): Полный путь к файлу.
        start_offset (int): Начальное смещение (включительно).
        end_offset (int): Конечное смещение (включительно).

    Returns:
        bytes: Последовательность байтов или None в случае ошибки.
    """
    # Проверка существования файла
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл '{file_path}' не найден.")
        return None

    # Проверка корректности диапазона
    if start_offset < 0 or end_offset < start_offset:
        print(f"Ошибка: Некорректный диапазон смещений ({start_offset}, {end_offset}).")
        return None

    try:
        file_size = os.path.getsize(file_path)
        if start_offset >= file_size:
            print(f"Ошибка: Начальное смещение ({start_offset}) выходит за пределы файла (размер {file_size} байт).")
            return None

        with open(file_path, 'rb') as f:
            f.seek(start_offset)
            # Рассчитываем количество байт для чтения
            num_bytes_to_read = min(end_offset - start_offset + 1, file_size - start_offset)
            if num_bytes_to_read <= 0:
                print("Ошибка: Нет байтов для чтения в заданном диапазоне.")
                return None
            data = f.read()
            return dataHex(data)

    except Exception as e:
        print(f"Ошибка при чтении файла '{file_path}': {e}")
        return None


"""  2E это .   619 байт не удалена (есть)
     2F это /   619 байт удалена (была)"""

# # ademHex = "41 33 46 46 44 30 35 43 2D 38 31 36 32 2D 34 44 39 44 2D 41 30 38 46 2D 42 37 45 45 41 45 38 36 39 45 43 35 7D 5C 41 44 45 4D 43 41 4D 34 4B 4F 4D 50 41 53 2E 41 44 4D "
# ademHex = "43 3A 5C 50 72 6F 67 72 61 6D 20 46 69 6C 65 73 5C 41 53 43 4F 4E 5C 4B 4F 4D 50 41 53 2D 33 44 20 76 32 33 5C 4C 69 62 73 5C 41 44 45 4D 34 4B 4F 4D 50 41 53 5C 56 61 75 6C 74 5C 49 4E 49 5C 74 64 6D 30 2E 69 6E "
#
# for file_path in listFiilPath:
#     hex_string: str
#     hex_string = read_bytes_at_offset(file_path, start_offset, end_offset)
#     hex2string = hex_string[hex_string.find("43 00 72 00 65 00 61 00 74 00 65 00 44 00 61 00 74 00 61 00 3D 00 "):].replace("43 00 72 00 65 00 61 00 74 00 65 00 44 00 61 00 74 00 61 00 3D 00 ", "")[12:][:2]
#     if hex2string == "2E":
#         print(f"\033[32mTrue                               {hex2string}        {hex_string[hex_string.find(ademHex):].replace(ademHex, "")[:2]}         {file_path}    ")
#     else:
#         print(f"\033[31mFalse                              {hex2string}        {hex_string[hex_string.find(ademHex):].replace(ademHex, "")[:2]}         {file_path}    ")

    # print("================")

# ademHex = "43 3A 5C 50 72 6F 67 72 61 6D 20 46 69 6C 65 73 5C 41 53 43 4F 4E 5C 4B 4F 4D 50 41 53 2D 33 44 20 76 32 33 5C 4C 69 62 73 5C 41 44 45 4D 34 4B 4F 4D 50 41 53 5C 56 61 75 6C 74 5C 49 4E 49 5C 74 64 6D 30 2E 69 6E 69"

def searchADEM(hex_string):
    resultDef = []
    hex2string = hex_string[hex_string.find("43 00 72 00 65 00 61 00 74 00 65 00 44 00 61 00 74 00 61 00 3D 00 "):].replace("43 00 72 00 65 00 61 00 74 00 65 00 44 00 61 00 74 00 61 00 3D 00 ", "")[12:][:2]

    ademHex = "43 3A 5C 50 72 6F 67 72 61 6D 20 46 69 6C 65 73 5C 41 53 43 4F 4E 5C 4B 4F 4D 50 41 53 2D 33 44 20 76 32 33 5C 4C 69 62 73 5C 41 44 45 4D 34 4B 4F 4D 50 41 53 5C 56 61 75 6C 74 5C 49 4E 49 5C 74 64 6D 30 2E 69 6E 69 "
    hexStringAdem = hex_string[hex_string.find(ademHex):].replace(ademHex, "")[:2]

    extensionAdemHex = "41 33 46 46 44 30 35 43 2D 38 31 36 32 2D 34 44 39 44 2D 41 30 38 46 2D 42 37 45 45 41 45 38 36 39 45 43 35 7D 5C 41 44 45 4D 43 41 4D 34 4B 4F 4D 50 41 53 2E 41 44 4D "
    hexStringExtensionAdem = hex_string[hex_string.find(extensionAdemHex):].replace(extensionAdemHex, "")[:10]

    if hexStringAdem == "00":
        resultDef.append(1)
    else:
        resultDef.append(0)

    if hex2string == "2E":
        resultDef.append(1)
    else:
        resultDef.append(0)

    if hexStringExtensionAdem[:2] == "41":
        resultDef.append(1)
    elif hexStringExtensionAdem[:2] == "0A":
        resultDef.append(0)
    else:
        if resultDef[0] != 0:
            print("hexStringExtensionAdem что то не так: {", hexStringExtensionAdem, "}")
        resultDef.append(0)

    return resultDef




def main(file_path):
    hex_string = read_bytes_at_offset(file_path)
    result = searchADEM(hex_string)

    sumResult = sum(result) / len(result)
    sumResult = float(str(sumResult)[:4])
    colorama.init()
    if sumResult == 0.0:
        print(Fore.RED,sumResult,Fore.WHITE, end="   |")
    elif sumResult == 1.0:
        print(Fore.GREEN, sumResult,Fore.WHITE, end="   |")
    else:
        print(Fore.YELLOW, sumResult,Fore.WHITE, end="  |")


    if not result[0]:
        print(Fore.RED,bool(result[0]), end=" ")
    else:
        print(Fore.GREEN, bool(result[0]), end="  ")

    if not result[1]:
        print(Fore.RED,bool(result[1]), end=" ")
    else:
        print(Fore.GREEN, bool(result[1]), end="  ")

    if not result[2]:
        print(Fore.RED,bool(result[2]),Fore.WHITE, end=" |")
    else:
        print(Fore.GREEN, bool(result[2]),Fore.WHITE, end="  |")

    print(Fore.WHITE, os.path.basename(file_path))

list_main_repo = []
main_repo = input(f"Введите путь к репозиторию, нажмите enter: ").strip()

while main_repo != "":
    main_repo = main_repo.replace("\\", "/")
    list_main_repo.append(main_repo)
    main_repo = input(f"Введите ещё путь к репозиторию, и\или нажмите enter: ")

for file_path in list_main_repo:
    main(file_path)

colorama.init()
print(Fore.WHITE+"Программа завершена. Нажмите Enter для закрытия.")
input()

