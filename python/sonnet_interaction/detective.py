import os
import string
from typing import List, Any

class Detective:
    RAW_PATH_TO_KLAYOUT: str = os.getcwd()
    FILE_PATH: str = os.path.join(RAW_PATH_TO_KLAYOUT, "EM", "sonnet-path.txt")

    @classmethod
    def _get_disk_list(cls) -> List[str]:
        """
        Возвращает список дисков, которые есть на компьютере.

        Возвращает:
        - Список строк, содержащих имена дисков на компьютере.
        """
        disk_list: List[str] = []
        for letter in string.ascii_uppercase:
            disk = letter + ':'
            if os.path.isdir(disk):
                disk_list.append(disk)
        return disk_list

    @classmethod
    def _get_path_to_sonnet(cls) -> str:
        """
        Возвращает путь до директории, в которой содержится файл emstatus.exe.

        Возвращает:
        - str: Путь до директории, в которой содержится файл emstatus.exe.
        - Если файл не найден, возвращает пустую строку.
        """
        filename = 'emstatus.exe'
        disk_list = cls._get_disk_list()
        for disk in disk_list:
            for root, _, filenames in os.walk(f'{disk}\\'):
                if filename in filenames:
                    return root
        return ''


    @classmethod
    def _get_path_from_file(cls, status: bool) -> str:
        """
        Возвращает строку, содержащую путь к файлу, либо записывает путь в файл и возвращает его.

        Аргументы:
        - status (bool): Если True, метод будет прочитывать файл по указанному пути и возвращать содержимое.
                         Если False, метод будет записывать путь к файлу в указанный файл и возвращать этот путь.

        Возвращает:
        - str: путь к файлу.
        """
        if status:
            with open(cls.FILE_PATH, "r") as file:
                return file.readline().strip()
        else:
            path = cls._get_path_to_sonnet()
            with open(cls.FILE_PATH, "w+") as file:
                file.write(path)
            return path

    @classmethod
    def file_processing(cls) -> str:
        """
        Создает папку "EM" в текущей директории, если ее не существует,
        затем читает путь из файла FILE_PATH, если он существует, иначе записывает путь в этот файл.
        
        Возвращает:
        - str: путь к файлу
        """
        em_folder_path = os.path.join(cls.RAW_PATH_TO_KLAYOUT, "EM")
        if not os.path.exists(em_folder_path):
            os.mkdir(em_folder_path)

        path_exists = os.path.exists(cls.FILE_PATH)
        return cls._get_path_from_file(path_exists)

    @classmethod
    def line_checker(cls, line_object):
        """
        Проверяет наличие пути в файле, и устанавливает его в QLineEdit объект, если он есть.

        Аргументы:
        - line_object: QLineEdit - объект в который нужно установить путь.
        """
        try:
            with open(cls.FILE_PATH, "r") as file:
                line_object.text = file.readline()
        except:
            line_object.placeholderText = r"Введите путь в формате: C:\Program Files\Sonnet Software\17.56\bin"
