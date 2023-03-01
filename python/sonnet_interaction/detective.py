import os
import string

class Detective:
    RAW_PATH_TO_KLAYOUT = r"{}".format(os.getcwd())
    FILE_PATH = RAW_PATH_TO_KLAYOUT + "\EM\sonnet-path.txt"

    @classmethod
    def __get_disk_list(self):
        disk_list = []
        for c in string.ascii_uppercase:
            disk = c + ':'
            if os.path.isdir(disk):
                disk_list.append(disk)
        return disk_list

    @classmethod
    def __get_path_to_sonnet(self): 
        filename = 'emstatus.exe'
        disk_list = self.__get_disk_list()
        for disk in disk_list:
            for root, _, filenames in os.walk(f'{disk}\\'):
                for file in filenames:
                    if file == filename:
                        return root

    @classmethod
    def __get_path_from_file(self, path_to_file, status):
        if status:
            with open(path_to_file, "r") as file:
                return file.readline()
        else:
            with open(path_to_file, "w+") as file:
                path = self.__get_path_to_sonnet()
                file.write(path)
                return path

    @classmethod
    def file_processing(self):
        if os.path.exists(self.RAW_PATH_TO_KLAYOUT + "\EM") == False:
            os.mkdir(self.RAW_PATH_TO_KLAYOUT + "\EM")

        return self.__get_path_from_file(self.FILE_PATH, os.path.exists(self.FILE_PATH))

    @classmethod
    def line_cheker(self, line_object):
        try:
            with open(self.FILE_PATH, "r") as file:
                line_object.text = file.readline()
        except:
            line_object.placeholderText = r"Введите путь в формате: C:\Program Files\Sonnet Software\17.56\bin"


