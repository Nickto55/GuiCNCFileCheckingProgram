import os


def is_adem_m3d_file(file_path, offset_start=0, offset_end=8192):
    """
    Проверяет, является ли файл .m3d файлом ADEM,
    проверяя наличие строки FullVersion=23 или выше в заданном диапазоне.

    Args:
        file_path (str): Полный путь к файлу.
        offset_start (int): Начальное смещение в байтах для поиска.
        offset_end (int): Конечное смещение в байтах для поиска.

    Returns:
        bool: True, если файл является ADEM .m3d, иначе False.
    """
    # Проверка существования файла
    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        return False

    try:
        with open(file_path, 'rb') as f:
            # Перемещаемся к начальному смещению
            f.seek(offset_start)
            # Читаем данные в заданном диапазоне
            # Убедимся, что не читаем больше, чем осталось в файле
            bytes_to_read = min(offset_end - offset_start, os.path.getsize(file_path) - offset_start)
            if bytes_to_read <= 0:
                # Диапазон поиска вне файла
                return False
            data = f.read(bytes_to_read)

        # --- Метод: Поиск строки FullVersion с версией >= 23 ---
        # Ищем подстроку 'FullVersion='
        fullversion_start = data.find(b'FullVersion=')
        if fullversion_start != -1:
            # Ограничиваем длину поиска, чтобы избежать проблем
            # Предполагаем, что номер версии находится в пределах 50 байт от начала строки
            version_data_end = min(fullversion_start + len('FullVersion=') + 50, len(data))
            version_data = data[fullversion_start + len('FullVersion='):version_data_end]

            # Пробуем декодировать как UTF-8 или Latin-1 (которая никогда не падает)
            # Данные могут быть в UTF-16, но часто ASCII-часть читается и так
            try:
                # Простая проверка: если видим "23." или "24." и т.д.
                version_str = version_data.decode('utf-8', errors='ignore')
                # Также проверим UTF-16 LE, так как в примерах были признаки UTF-16
                version_str_utf16 = version_data.decode('utf-16le', errors='ignore')

                # Проверяем обе декодированные строки на наличие номера версии >= 23
                for v_str in [version_str, version_str_utf16]:
                    # Простой способ: ищем "23." или "24." ... "99." в начале строки версии
                    # Это работает для версий 23.0, 23.0.6.2318, 24.1 и т.д.
                    if any(v_str.strip().startswith(str(i) + '.') for i in range(23, 100)):
                        return True
            except (UnicodeDecodeError, IndexError):
                # Если не удалось декодировать, пробуем другие методы
                pass

        # Если строка FullVersion не найдена или не подходит, файл не ADEM
        return False

    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return False


"""  2E это .   619 байт не удалена (есть)
     2F это /   619 байт удалена (была)"""

file1 = r"C:\Users\yakovlev_nd\Documents\ЛТИЯ.758442.007 Гайка().m3d"
file2 = r"C:\Users\yakovlev_nd\Documents\ЛТИЯ.758442.007 Гайка(проект ADEM).m3d"
# file3 = r"C:\Users\yakovlev_nd\Documents\ЛТИЯ.758442.007 Гайка(v21).m3d"

print(f"{file1} является ADEM файлом: {is_adem_m3d_file(file1, 418, 470)}")
print(f"{file2} является ADEM файлом: {is_adem_m3d_file(file2, 418, 470)}")
