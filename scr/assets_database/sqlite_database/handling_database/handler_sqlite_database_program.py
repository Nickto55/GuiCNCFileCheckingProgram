from scr.assets_database.sqlite_database.receiver_sqlite_database import ReceiverDataBase


class SQLiteDatabaseProgrammData:
    def __init__(self):
        self.data_base = ReceiverDataBase()
        self.name_dict = 'program data'

    def get_all_db_program(self):
        """
        Возвращает данные в формате вложенного словаря,
        чтобы остальной код приложения не сломался.
        """
        rows = self.data_base.get_all_rows()
        result = {}
        for row in rows:
            machine = row['name_machine_directory']
            dse_dir = row['dse_directory']
            dse_name = row['dse_name']

            result.setdefault(machine, {}).setdefault(dse_dir, {})[dse_name] = {
                'dse_name': dse_name,
                'content': row['content'],
                'link': row['link'],
                'fm_file': row['fm_file'],
                'files_without_extension': row['files_without_extension'],
                'last_modified_date': row['last_modified_date'],
                'kb': row['kb']
            }
        return result

    def get_program_data(self, repository_name):
        """Получить данные по конкретному DSE (работает мгновенно благодаря индексу)."""
        rows = self.data_base.get_rows_by_dse_name(repository_name)
        return [dict(row) for row in rows]

    def set_program_db(
            self
            , name_machine_directory
            , dse_directory
            , dse_name
            , content=''
            , link=''
            , fm_file=''
            , files_without_extension=''
            , last_modified_date=''
            , kb=''
    ):
        """
        Записывает или обновляет данные.
        Больше не нужно читать весь файл, проверять ключи и писать его обратно!
        """
        existing = self.data_base.get_rows_by_dse_name(dse_name)
        if existing:
            old = existing[0]
            if not content: content = old['content']
            if not link: link = old['link']
            if not fm_file: fm_file = old['fm_file']
            if not files_without_extension: files_without_extension = old['files_without_extension']
            if not last_modified_date: last_modified_date = old['last_modified_date']
            if not kb: kb = old['kb']

        self.data_base.upsert_program_data(
            name_machine_directory=name_machine_directory,
            dse_directory=dse_directory,
            dse_name=dse_name,
            content=content,
            link=link,
            fm_file=fm_file,
            files_without_extension=files_without_extension,
            last_modified_date=last_modified_date,
            kb=kb
        )

    def __del__(self):
        if hasattr(self, 'data_base'):
            self.data_base.close()


if __name__ == "__main__":
    app = SQLiteDatabaseProgrammData()

    app.set_program_db(
        name_machine_directory='HAAS',
        dse_directory='БАШК',
        dse_name='БАШК.711112.003',
        content='',
        link=r'//Dc-hv-disp/UP/HAAS\БАШК\БАШК.711112.003',
        fm_file='X',
        files_without_extension='',
        last_modified_date='2016-04-07 14:29:57',
        kb='POPOVCHENKO S.S. )'
    )

    print('---------------------------------------------------')
    # Тест чтения
    # all_data = app.get_all_db_program()
    # for i, l in all_data.items():
    #     for j, k in l.items():
    #         print(i, j, k)