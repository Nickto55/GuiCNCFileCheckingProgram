import os
import time
import openpyxl
from datetime import date

from scr.assets_excel.enters.excel_enter import ExcelEnter
from scr.handling.author_verification_program import main as author_main
from scr.handling.application_data_checker import main as application_data_checker_main

# from scr.assets_database.json_database.handling_database.handler_json_database_program import DatabaseProgrammData
from scr.assets_database.sqlite_database.handling_database.handler_sqlite_database_program import \
    SQLiteDatabaseProgrammData

list_spli = []
recursion_depth = 2
today = date.today()


class ProgressTracker:
    """
    Трекер прогресса без привязки к GUI.

    Принимает callback-функции:
        progress_callback(percent, message)
        log_callback(message)

    Это позволяет использовать его в любом месте:
    в GUI, в консоли, в тестах.
    """

    def __init__(
            self
            , progress_callback=None
            , log_callback=None
            , segment_start_percent=0.0
            , segment_size_percent=100.0
    ):
        self.progress_callback = progress_callback
        self.log_callback = log_callback

        self.segment_start_percent = float(segment_start_percent)
        self.segment_size_percent = float(segment_size_percent)

        self.total_steps = 0
        self.current_step = 0

    def set_total(self, total_steps):
        """
        Устанавливает общее количество внутренних шагов.
        """
        try:
            self.total_steps = int(total_steps)
        except Exception:
            self.total_steps = 0

        if self.total_steps < 0:
            self.total_steps = 0

        self.current_step = 0

    def update(self, current_internal_step, message):
        """
        Обновляет прогресс внутри сегмента текущей программы.

        current_internal_step: текущий внутренний шаг
        message: сообщение для логов/прогресс-бара
        """
        try:
            self.current_step = int(current_internal_step)
        except Exception:
            self.current_step = 0

        if self.total_steps > 0:
            internal_progress_ratio = self.current_step / float(self.total_steps)
        else:
            internal_progress_ratio = 0.0

        if internal_progress_ratio < 0:
            internal_progress_ratio = 0.0

        if internal_progress_ratio > 1:
            internal_progress_ratio = 1.0

        overall_progress_percent = (
                self.segment_start_percent +
                internal_progress_ratio * self.segment_size_percent
        )

        if overall_progress_percent < self.segment_start_percent:
            overall_progress_percent = self.segment_start_percent

        if overall_progress_percent > self.segment_start_percent + self.segment_size_percent:
            overall_progress_percent = self.segment_start_percent + self.segment_size_percent

        overall_progress_percent = int(overall_progress_percent)

        if self.progress_callback:
            self.progress_callback(overall_progress_percent, message)

        if self.log_callback:
            self.log_callback(message)


class LogicCncProgram:
    def __init__(self):
        self.list_spli = []
        self.recursion_depth = 2
        self.today = date.today()

    def collect_subdirectories(
            self
            , root_dir_list: list
            , progress_tracker=None
    ):
        result = {}

        if progress_tracker:
            progress_tracker.set_total(len(root_dir_list))

        if not root_dir_list:
            if progress_tracker:
                progress_tracker.update(0, "Обработка директорий завершена")
            return result

        count = 0

        for dir_name in root_dir_list:
            if progress_tracker:
                progress_tracker.update(
                    count
                    , f"Обработка директории: {os.path.basename(dir_name)}"
                )

            project_path = dir_name

            print(f"Создание листа: {os.path.basename(dir_name)}...")

            subdirs = []

            def recurse(path):
                try:
                    for item in os.listdir(path):
                        full_path = os.path.join(path, item)

                        if os.path.isdir(full_path):
                            if full_path.count("\\") == self.recursion_depth:
                                subdirs.append({
                                    "name": item
                                    , "content": ""
                                    , "full_path": full_path
                                })

                            recurse(full_path)

                        if full_path.count("\\") == self.recursion_depth + 1:
                            parent_dir = os.path.basename(os.path.dirname(full_path))
                            subdirs.append({
                                "name": parent_dir
                                , "content": item
                                , "full_path": full_path
                            })

                except PermissionError:
                    print(f"Не удалось получить доступ к {path}")

            recurse(project_path)

            result[os.path.basename(dir_name)] = subdirs
            count += 1

        if progress_tracker:
            progress_tracker.update(
                len(root_dir_list)
                , "Обработка директорий завершена"
            )

        return result

    def main_cnc_file_checking_program(
            self
            , list_main_repo: list
            , chose_user: int
            , two_programm: int
            , progress_tracker=None
            , count_prog=1
            , output_file: str = None
    ):
        """
        Основная программа обработки директорий.

        Возвращает полный путь к созданному Excel-файлу
        или None, если файл не был создан.
        """
        print([chose_user, count_prog])

        current_directory = os.getcwd()

        config_dir = os.path.join(os.path.expanduser("~"), ".CNCFileCheckingProgram")

        def name_user_see(config_path):
            user_name = ""
            count = 0

            for i in config_path:
                if i == os.sep:
                    if count < 3:
                        count += 1
                    else:
                        break

                if count == 2 and i != os.sep:
                    user_name += i

            return user_name

        name_user_see(config_dir)

        if output_file:
            output_file = str(output_file).strip()
        else:
            output_file = f"BD_CNCprog_{self.today}"

        if not output_file.lower().endswith(".xlsx"):
            output_file += ".xlsx"

        if os.path.isabs(output_file):
            full_output_path = os.path.abspath(output_file)
        else:
            full_output_path = os.path.join(current_directory, output_file)

        output_dir = os.path.dirname(full_output_path)

        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                print(f"Не удалось создать директорию для файла: {e}")

        if not list_main_repo:
            print("Не указано ни одного репозитория.")

            if two_programm:
                try:
                    wb = openpyxl.Workbook()

                    if "Sheet" in wb.sheetnames:
                        del wb["Sheet"]

                    wb.save(full_output_path)

                    print(f"Создан пустой файл: {full_output_path}")

                    return full_output_path

                except Exception as e:
                    print(f"Ошибка при создании пустого файла: {e}")
                    return None

            return None

        self.recursion_depth = 2

        data = self.collect_subdirectories(
            list_main_repo,
            progress_tracker
        )
        # self.filling_database(data)
        try:
            print('full_output_path', full_output_path)
            ExcelEnter().save_to_excel(data, full_output_path)
        except Exception as e:
            print(
                f"cnc_file_checking_program. main_cnc_file_checking_program.Ошибка при сохранении файла в mainCNCFileCheckingProgram: {e}")
            return None

        return full_output_path

    @staticmethod
    def filling_database(data):
        """
        Функция заполняет базу данных
        """
        for name_machine_directory, data_machine_directory in data.items():
            for data_dse in data_machine_directory:
                dse_name = data_dse.get('name', '')
                content = data_dse.get('content', '')
                try:
                    link = os.path.normpath(str(data_dse.get('full_path', '')))  # Полный путь
                except:
                    link = str(data_dse.get('full_path', ''))  # Полный путь
                fm_file = data_dse.get('fm_file', '')
                files_without_extension = data_dse.get('files_without_extension', '')
                last_modified_date = data_dse.get('last_modified_date', '')
                kb = data_dse.get('kb', '')

                normalized_link = link.replace('\\', '/')
                normalized_machine = name_machine_directory.replace('\\', '/')

                name_dse_directory = ""
                try:
                    start_idx = normalized_link.index(normalized_machine) + len(normalized_machine) + 1

                    end_idx = normalized_link.index(dse_name, start_idx) - 1

                    if start_idx < end_idx:
                        name_dse_directory = normalized_link[start_idx:end_idx]
                except ValueError:
                    pass

                database_json_program = SQLiteDatabaseProgrammData()
                database_json_program.set_program_db(
                    name_machine_directory=name_machine_directory
                    , dse_directory=name_dse_directory
                    , dse_name=dse_name
                    , content=content
                    , link=normalized_link
                    , fm_file=fm_file
                    , files_without_extension=files_without_extension
                    , last_modified_date=last_modified_date
                    , kb=kb
                )


def main_cnc_file_checking_program(
        list_main_repo: list
        , chose_user: int
        , two_programm: int
        , progress_tracker=None
        , count_prog=1
        , output_file: str = None
):
    """
    Совместимая обёртка для вызова основной программы обработки директорий.
    """

    return LogicCncProgram().main_cnc_file_checking_program(
        list_main_repo=list_main_repo
        , chose_user=chose_user
        , two_programm=two_programm
        , progress_tracker=progress_tracker
        , count_prog=count_prog
        , output_file=output_file
    )


def run_program(
        run_cnc: bool
        , run_data: bool
        , run_author: bool
        , output_file: str
        , directories: list
        , log_callback=None
        , progress_callback=None
):
    """
    Запуск выбранных программ.

    Этот метод не знает про tkinter/GUI.
    Он только выполняет логику и отправляет сообщения через callback.
    """

    def _log(message):
        if log_callback:
            log_callback(message)
        else:
            print(message)

    def _progress(percent, text):
        if progress_callback:
            progress_callback(percent, text)

    total_steps = sum([
        bool(run_cnc)
        , bool(run_data)
        , bool(run_author)
    ])

    start_time = time.time()

    result_file = output_file

    print("output_file", output_file)

    _log("Запуск выбранных программ:")

    if run_cnc:
        _log("- Программа обработки директорий")

    if run_data:
        _log("- Программа создания сводной таблицы")

    if run_author:
        _log("- Программа отображения авторов")

    _log(f"Выходной файл: {output_file}")

    if total_steps == 0:
        _progress(100, "Завершено!")
        _log("Все выбранные операции завершены!")

        if result_file and not os.path.isabs(result_file):
            result_file = os.path.abspath(result_file)

        return {
            "file_to_open": result_file,
            "execution_time": 0
        }

    current_step = 0
    logic = LogicCncProgram()

    # Шаг 1: Программа обработки директорий
    if run_cnc:
        segment_start_percent = (current_step / total_steps) * 100
        segment_size_percent = (1 / total_steps) * 100
        current_step += 1

        progress_text = f"Выполнение обработки директорий... ({current_step}/{total_steps})"

        _progress(segment_start_percent, progress_text)
        _log("Выполнение программы обработки директорий...")

        tracker = ProgressTracker(
            progress_callback=_progress
            , log_callback=_log
            , segment_start_percent=segment_start_percent
            , segment_size_percent=segment_size_percent
        )

        if not directories:
            warning_msg = (
                "Предупреждение: Выбрано использование сохраненных директорий, "
                "но список пуст. Пропуск обработки."
            )

            _log(warning_msg)
            _progress(
                segment_start_percent + segment_size_percent,
                "Пропущено: Нет директорий"
            )

        else:
            returned_file = logic.main_cnc_file_checking_program(
                list_main_repo=directories
                , chose_user=1
                , two_programm=1 if run_data else 0
                , progress_tracker=tracker
                , count_prog=1
                , output_file=output_file
            )

            if returned_file is None:
                print(returned_file, "Программа обработки директорий не вернула имя файла.")
                raise Exception("Программа обработки директорий не вернула имя файла.")

            result_file = returned_file

    # Шаг 2: Программа создания сводных таблиц
    if run_data:
        segment_start_percent = (current_step / total_steps) * 100
        segment_size_percent = (1 / total_steps) * 100
        current_step += 1

        progress_text = f"Создание сводных таблиц... ({current_step}/{total_steps})"

        _progress(segment_start_percent, progress_text)
        _log("Создание сводной таблицы...")

        tracker = ProgressTracker(
            progress_callback=_progress
            , log_callback=_log
            , segment_start_percent=segment_start_percent
            , segment_size_percent=segment_size_percent
        )

        # try:
        full_output_path = application_data_checker_main(
            output_file
            , progress_tracker=tracker
        )

        _log("Обработка завершена. Лист 'ДСЕ по станкам' создан.")

        _progress(
            segment_start_percent + segment_size_percent,
            "Создание сводных таблиц завершено"
        )

        if isinstance(full_output_path, str) and full_output_path:
            result_file = full_output_path

        # except Exception as e:
        #     error_msg = f"Ошибка в программе создания сводных таблиц: {str(e)}"
        #
        #     _log(error_msg)
        #
        #     _progress(
        #         segment_start_percent + segment_size_percent,
        #         f"Ошибка в сводных таблицах: {type(e).__name__}"
        #     )

    # Шаг 3: Программа отображения авторов
    if run_author:
        segment_start_percent = (current_step / total_steps) * 100
        segment_size_percent = (1 / total_steps) * 100
        current_step += 1

        progress_text = f"Отображение авторов... ({current_step}/{total_steps})"

        _progress(segment_start_percent, progress_text)
        _log("Выполнение программы отображения авторов...")

        tracker = ProgressTracker(
            progress_callback=_progress
            , log_callback=_log
            , segment_start_percent=segment_start_percent
            , segment_size_percent=segment_size_percent

        )

        try:
            author_result = author_main(
                excel_file=output_file
                , db_handler=logic
                , progress_tracker=tracker
            )

            _log("Программа отображения авторов завершена!")

            _progress(
                segment_start_percent + segment_size_percent,
                "Отображение авторов завершено"
            )

            if isinstance(author_result, str) and author_result:
                result_file = author_result

        except Exception as e:
            error_msg = f"Ошибка в программе отображения авторов: {str(e)}"

            _log(error_msg)

            _progress(
                segment_start_percent + segment_size_percent,
                f"Ошибка в отображении авторов: {type(e).__name__}"
            )

            raise

    _progress(100, "Завершено!")
    _log("Все выбранные операции завершены!")

    file_to_open = result_file if result_file else output_file

    if file_to_open and not os.path.isabs(file_to_open):
        file_to_open = os.path.abspath(file_to_open)

    end_time = time.time()
    execution_time = end_time - start_time

    return {
        "file_to_open": file_to_open,
        "execution_time": execution_time
    }


if __name__ == "__main__":
    app = LogicCncProgram()
    # app.collect_subdirectories(
    #     root_dir_list=[
    #         r'C:\Users\yakovlev_nd\Desktop\Tests\CNCFileCheckingProgram\Dashid',
    #
    #         r'C:\Users\yakovlev_nd\Desktop\Tests\CNCFileCheckingProgram\HAAS'
    #     ],
    #     progress_tracker=None,
    #     lastTimeAuvtoSearchBool=True
    # )
