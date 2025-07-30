import webbrowser

from openpyxl.styles.builtins import output
from AuthorVerificationProgram import main
from ApplicationDataChecker import mainApplicationDataChecker
from CNCFileCheckingProgram import mainCNCFileCheckingProgram, today
from Config import outputFileDef
from  useJson import jsonDir

class MainCNCprogramme:
    outputFile: str
    choseYes: list = ["Y", "y"]
    choseNo: list = ["N", "n"]

    def __init__(self):
        MainCNCprogramme.main(self)

    def choseUserYN(self, inputChosetxt):
        self.inputChose = input(f" ~ Вы хотите {inputChosetxt} сохранённые репозитории? [Y/N]: ")
        if self.choseYes.count(self.inputChose) > 0 or self.choseNo.count(self.inputChose) > 0:
            if self.choseYes.count(self.inputChose) > 0:
                return 1
            if self.choseNo.count(self.inputChose) > 0:
                return 0
        MainCNCprogramme.choseUserYN(self, inputChosetxt)

    def choseUserScenarios(self):
        try:
            choseUser = int(input(" ~ Выберите один из 5 вариантов: \n   1.Работает только программа обработки директорий.\n   2.Работают программа обработки директорий и программа создание сводных таблиц.\n   3.Работает программа отображения авторов nc и h файлов.\n   4.Работают программы программы обработки директорий и отображения авторов.\n   5.Работают все программы.\n ~ Введите цифру (1/2/3/4/5): "))
            if 5 >= choseUser >= 1:
                return choseUser
            return MainCNCprogramme.choseUserScenarios(self)
        except:
            print("Введите цифры, от 1, до 5.")
            return MainCNCprogramme.choseUserScenarios(self)


    def main(self):
        output_file = f"BD_CNCprog_{today}"
        if not output_file.endswith(".xlsx"):
            output_file += ".xlsx"
        choseUserProgramme = MainCNCprogramme.choseUserScenarios(self)
        choseUserChangeDir = MainCNCprogramme.choseUserYN(self, "изменить")
        if choseUserChangeDir:
            jsonDir(0)
        choseUserUseSaveDir = MainCNCprogramme.choseUserYN(self,"использовать")

        if choseUserProgramme == 1:
            if choseUserUseSaveDir:
                mainCNCFileCheckingProgram(jsonDir.code(self), 1, 0)
            else:
                mainCNCFileCheckingProgram(list(), 0,0)
        elif choseUserProgramme == 2:
            if choseUserUseSaveDir:
                output_file = mainCNCFileCheckingProgram(jsonDir.code(self), 1, 1)
            else:
                output_file = mainCNCFileCheckingProgram(list(), 0,1)
            print(f"Программа CNCFileCheckingProgram завершена. Создание сводной таблицы...")
            full_output_path = mainApplicationDataChecker(output_file)
            print(f"Обработка завершена. Лист 'ДЕ по станкам' создан.")
            # Stop для программы
            stopKod = input(
                f"Нажмите Enter для  запуска файла, или введите любой символ, а затем Enter, для того чтобы не запускать: ")
            if stopKod == "":
                webbrowser.open(full_output_path)
        elif choseUserProgramme == 3:
            main(output_file)
        elif choseUserProgramme == 4:
            if choseUserUseSaveDir:
                mainCNCFileCheckingProgram(jsonDir.code(self), 1, 1)
            else:
                mainCNCFileCheckingProgram(list(), 0, 1)
            main(output_file)
        else:
            if choseUserUseSaveDir:
                output_file = mainCNCFileCheckingProgram(jsonDir.code(self), 1, 1)
            else:
                output_file = mainCNCFileCheckingProgram(list(), 0, 1)
            print(f"Программа CNCFileCheckingProgram завершена. Создание сводной таблицы...")
            full_output_path = mainApplicationDataChecker(output_file)
            print(f"Обработка завершена. Лист 'ДЕ по станкам' создан.")
            # Stop для программы
            stopKod = input(
                f"Нажмите Enter для  запуска файла, или введите любой символ, а затем Enter, для того чтобы не запускать: ")
            main(output_file)



if __name__ == '__main__':
    MainCNCprogramme()