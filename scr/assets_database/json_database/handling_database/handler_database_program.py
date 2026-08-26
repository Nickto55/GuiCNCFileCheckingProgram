import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scr.assets_database.json_database.receiver_db import ReceiverDataBase


class DatabaseProgrammData:
    def __init__(self):
        self.data_base = ReceiverDataBase()
        self.name_dict = 'program data'

    def get_all_db_program(self):
        self.data_base.load()
        return self.data_base.data.get(self.name_dict, '')

    def set_db_progrm(self, key, data):
        if key in self.data_base.data.get(self.name_dict, '').keys():
            self.data_base.data[self.name_dict][key] = data
            self.data_base.save()
            self.data_base.load()

    def get_program_data(self, repository_name):
        self.data_base.load()
        return self.data_base.data[self.name_dict].get(repository_name, '')

    def set_program_db(
            self
            , name_machine_directory
            , dse_directory
            , dse_name
            # , data_dse=None
            , content=''
            , link=''
            , fm_file=''
            , files_without_extension=''
            , last_modified_date=''
            , kb=''
    ):
        data_program = self.get_all_db_program()
        if name_machine_directory in self.data_base.data[self.name_dict].keys():
            data_database_machine_directory = self.data_base.data[self.name_dict][name_machine_directory]
            # print(data_database_machine_directory)
            if dse_directory in data_database_machine_directory.keys():
                data_in_database_dse = data_database_machine_directory[dse_directory]
                if dse_name in data_in_database_dse.keys():
                    data_in_database_dse_name = data_in_database_dse[dse_name]

                    bd_content = data_in_database_dse_name.get('url git', '')
                    bd_link = data_in_database_dse_name.get('last version', '')
                    bd_fm_file = data_in_database_dse_name.get('comment', '')
                    bd_files_without_extension = data_in_database_dse_name.get('name', '')
                    bd_last_modified_date = data_in_database_dse_name.get('target', '')
                    bd_kb = data_in_database_dse_name.get('date relise', '')

                    if content == '' and bd_content != '': content = bd_content
                    if link == '' and bd_link != '': link = bd_link
                    if fm_file == '' and bd_fm_file != '': fm_file = bd_fm_file
                    if files_without_extension == '' and bd_files_without_extension != '': files_without_extension = bd_files_without_extension
                    if last_modified_date == '' and bd_last_modified_date != '': last_modified_date = bd_last_modified_date
                    if kb == '' and bd_kb != '': kb = bd_kb
                else:
                    data_program[name_machine_directory][dse_directory][dse_name] = {}
            else:
                data_program[name_machine_directory][dse_directory] = {}
                data_program[name_machine_directory][dse_directory][dse_name] = {}

        if name_machine_directory in data_program.keys():
            data_name_machine_directory = data_program.get(name_machine_directory)
            data_dse_directory = data_name_machine_directory.get(dse_directory)
            data_dse_directory.update(
                {
                    dse_name: {
                        'dse_name': dse_name
                        , 'content': content
                        , 'link': link
                        , 'fm_file': fm_file
                        , 'files_without_extension': files_without_extension
                        , 'last_modified_date': last_modified_date
                        , 'kb': kb
                    }
                }
            )

            data_name_machine_directory.update({dse_directory: data_dse_directory})
            data_program.update({name_machine_directory: data_name_machine_directory})
        else:
            data_program={
                name_machine_directory:{
                    dse_directory:{
                        dse_name: {
                            'dse_name': dse_name
                            , 'content': content
                            , 'link': link
                            , 'fm_file': fm_file
                            , 'files_without_extension': files_without_extension
                            , 'last_modified_date': last_modified_date
                            , 'kb': kb
                        }
                    }
                }
            }

        self.data_base.data[self.name_dict].update(data_program)
        self.data_base.save()
        self.data_base.load()


if __name__ == "__main__":
    app = DatabaseProgrammData()
    app.set_program_db(
        name_machine_directory='HAAS'
        , dse_directory='БАШК'
        , dse_name='БАШК.711112.003'
        # ,data_dse=''
        , content=''
        , link=r'//Dc-hv-disp/UP/HAAS\БАШК\БАШК.711112.003'
        , fm_file='X'
        , files_without_extension=''
        , last_modified_date='2016-04-07 14:29:57'
        , kb='POPOVCHENKO S.S. )'

    )

    print('---------------------------------------------------')
    print(app.get_all_db_program())
    print('---------------------------------------------------')
    for i, l in app.get_all_db_program().items():
        for j, k in l.items():
            print(i, j, k)
