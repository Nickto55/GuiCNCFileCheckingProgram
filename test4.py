import os


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


file_path1 = r"C:\Users\yakovlev_nd\Documents\ЛТИЯ.758442.007 Гайка().m3d"
file_path2 = r"C:\Users\yakovlev_nd\Documents\ЛТИЯ.758442.007 Гайка(v21).m3d"
file_path3 = r"C:\Users\yakovlev_nd\Documents\ЛТИЯ.758442.007 Гайка(v21).m3d"

hex_string1 = read_bytes_at_offset(file_path1)
hex_string2 = read_bytes_at_offset(file_path2)
hex_string3 = read_bytes_at_offset(file_path3)

hex_list1 = hex_string1.split(" ")
hex_list2 = hex_string2.split(" ")
hex_list3 = hex_string3.split(" ")


def comparisonList(list1: list, list2: list, list3: list):
    for i in range(max(len(list1),len(list2),len(list3))):
        if i < min(len(list1),len(list2),len(list3)):
            if list1[i]==list2[i]== list3[i]:
                print(f"\033[32m {i:>{len(str(max(len(list1),len(list2))))}} |{hex(i)}| {list1[i]} {list2[i]}")
            else:
                print(f"\033[31m {i:>{len(str(max(len(list1),len(list2))))}} | {list1[i]} {list2[i]}")


comparisonList(hex_list1, hex_list2, hex_list3)


