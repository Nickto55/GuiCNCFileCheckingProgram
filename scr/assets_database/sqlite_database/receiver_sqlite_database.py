import os
import sqlite3
import shutil


class ReceiverDataBase:
    def __init__(self, name_file_db=None):
        self.name_programm_config_dir = ".CNCDirCheckingProgram"
        self.name_work_dir = 'configs'

        self.name_work_file = name_file_db if name_file_db is not None else 'database.db'

        self.CONFIG_DIR = os.path.join(os.path.expanduser("~"), self.name_work_dir, self.name_programm_config_dir)
        self.file_path = os.path.join(self.CONFIG_DIR, self.name_work_file)

        os.makedirs(self.CONFIG_DIR, exist_ok=True)

        self.conn = sqlite3.connect(self.file_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

        self._create_table()

    def _create_table(self):
        """Создает таблицу, если её нет."""
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS program_data (
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
        self.cur.execute('CREATE INDEX IF NOT EXISTS idx_machine ON program_data(name_machine_directory)')
        self.cur.execute('CREATE INDEX IF NOT EXISTS idx_dse_name ON program_data(dse_name)')
        self.conn.commit()

    def save(self):
        """В SQLite сохранение происходит через commit."""
        self.conn.commit()

    def load(self):
        """В SQLite этот метод не нужен, данные всегда актуальны."""
        pass

    def get_all_rows(self):
        """Получить все записи из БД (сырой список)."""
        self.cur.execute("SELECT * FROM program_data")
        return self.cur.fetchall()

    def get_rows_by_dse_name(self, repository_name):
        """Быстрый поиск по имени DSE."""
        self.cur.execute("SELECT * FROM program_data WHERE dse_name = ?", (repository_name,))
        return self.cur.fetchall()

    def upsert_program_data(self, name_machine_directory, dse_directory, dse_name,
                            content, link, fm_file, files_without_extension,
                            last_modified_date, kb):
        """
        Вставка или обновление записи (UPSERT).
        Если такая комбинация machine/dse_dir/dse_name уже есть - обновит. Если нет - создаст.
        """
        query = '''
            INSERT INTO program_data 
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