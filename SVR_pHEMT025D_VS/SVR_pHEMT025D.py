#Запускаем в режиме отладки
import subprocess
import shutil
from pathlib import Path
print("Отладка библиотеки")
#Скопируем текущую билиотеку по пути в KLayout
HomeDir=Path.home()# пользовательская папка
print(HomeDir)
DestinationDir= str(HomeDir)+r"\KLayout\salt\SVR_pHEMT025D"
SourceDir=r"..\SVR_pHEMT025D"
KLayoutPath=str(HomeDir)+r"\AppData\Roaming\KLayout\klayout_app.exe"
shutil.copytree(SourceDir,DestinationDir,dirs_exist_ok=True)
print("Библиотека скопирована в "+ DestinationDir)
#Запустим KLayout
print("Запускаем KLayout...")
subprocess.run(KLayoutPath)
