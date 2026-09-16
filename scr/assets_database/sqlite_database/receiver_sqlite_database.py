import os
import sqlite3

import pandas as pd


class ReceiverDataBase:
    def __init__(self, name_file_db=None, name_tabel=None):
        # name_programm_config_dir = ".CNCDirCheckingProgram"
        # name_work_dir = 'configs'
        self.name_tabel = name_tabel if not pd.isna(name_tabel) or name_tabel == '' else 'NO_NAME_TABEL'

        name_work_file = name_file_db if name_file_db is not None else 'summary_table_of_milling_machines.db'

        # self.config_dir = os.path.join(os.path.expanduser("~"), name_work_dir, name_programm_config_dir)
        config_dir = r'\\volna.dmn\data\obmen\Служба Главного инженера\ОГТ\ЧПУ\Программы Python\database_program'
        self.file_path = os.path.join(config_dir, name_work_file)

        os.makedirs(config_dir, exist_ok=True)

        self.conn = sqlite3.connect(self.file_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

        self._create_table()

    def _create_table(self):
        """Создает таблицу, если её нет."""
        self.cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.name_tabel} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_machine_directory TEXT NOT NULL,
                dse_directory TEXT NOT NULL,
                dse_name TEXT NOT NULL,
                content TEXT DEFAULT '',
                link TEXT DEFAULT '',
                fm_file TEXT DEFAULT '',
                files_without_extension TEXT DEFAULT '',
                last_modified_date TEXT DEFAULT '',
                kb TEXT DEFAULT '',
                UNIQUE(name_machine_directory, dse_directory, dse_name)
            )
        ''')
        # Создаем индексы для ускорения поиска
        self.cur.execute(f'CREATE INDEX IF NOT EXISTS idx_machine ON {self.name_tabel}(name_machine_directory)')
        self.cur.execute(f'CREATE INDEX IF NOT EXISTS idx_dse_name ON {self.name_tabel}(dse_name)')
        self.conn.commit()

    def save(self):
        """В SQLite сохранение происходит через commit."""
        self.conn.commit()

    def load(self):
        """В SQLite этот метод не нужен, данные всегда актуальны."""
        pass

    def get_all_rows(self):
        """Получить все записи из БД (сырой список)."""
        self.cur.execute(f"SELECT * FROM {self.name_tabel}")
        return self.cur.fetchall()

    def get_rows_by_dse_name(self, repository_name):
        """Быстрый поиск по имени DSE."""
        self.cur.execute(f"SELECT * FROM {self.name_tabel} WHERE dse_name = ?", (repository_name,))
        return self.cur.fetchall()

    def upsert_program_data(self, name_machine_directory, dse_directory, dse_name,
                            content, link, fm_file, files_without_extension,
                            last_modified_date, kb):
        """
        Вставка или обновление записи (UPSERT).
        Если такая комбинация machine/dse_dir/dse_name уже есть - обновит. Если нет - создаст.
        """
        query = f'''
            INSERT INTO {self.name_tabel} 
            (name_machine_directory, dse_directory, dse_name, content, link, fm_file, 
             files_without_extension, last_modified_date, kb)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name_machine_directory, dse_directory, dse_name) 
            DO UPDATE SET 
                content=excluded.content,
                link=excluded.link,
                fm_file=excluded.fm_file,
                files_without_extension=excluded.files_without_extension,
                last_modified_date=excluded.last_modified_date,
                kb=excluded.kb;
        '''
        self.cur.execute(query, (
            name_machine_directory, dse_directory, dse_name, content, link,
            fm_file, files_without_extension, last_modified_date, kb
        ))
        self.conn.commit()

    def close(self):
        self.conn.close()
