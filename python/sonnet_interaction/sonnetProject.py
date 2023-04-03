from datetime import datetime
import os
import re
import sys
import pya
import math
RAW_PATH_TO_KLAYOUT = r"{}".format(os.getcwd())
TRANS_TABLE_LAYERS = {'Met1': 'Met1u', 'Met2':'Met2u', '80/7': 'TFR1', '81/8': 'TFR2',
                      '82/9': 'TFR3', '91/10': 'Met1u', '71/11': 'Via2', '92/13': 'Met2u'}


class Handler:
    @classmethod
    def insert_list_to_file(self, path_to_file, list):
        with open(path_to_file, "w+") as file:
            for str in list:
                file.write(str)
                file.write("\n")
        file.close()

    @classmethod    
    def insert_nested_list_to_file(self, path_to_file, nested_list):
        with open(path_to_file, "w+") as file:
            for block in nested_list:
                for str in block:
                    file.write(str)
                    file.write("\n")
        
class BatFile:
    def __init__(self, file_name, local_path_to_dir):
        self.file_name = file_name
        self.file_dir_path = RAW_PATH_TO_KLAYOUT + local_path_to_dir

    def create_file(self):
        Handler.insert_list_to_file(self.file_dir_path + "\\" + self.file_name + ".bat", self.text)

        os.chdir(self.file_dir_path)
        os.system(f"start {self.file_name}")
        os.chdir(RAW_PATH_TO_KLAYOUT)
        
class BatModeling(BatFile):
    def __init__(self, file_name, local_path_to_dir, path_to_sonnet):
        super().__init__(file_name, local_path_to_dir)
        self.file_dir_path = RAW_PATH_TO_KLAYOUT + local_path_to_dir + "\\" + file_name
        self.text = [
            "@echo off",
            rf"cd {path_to_sonnet}",
            rf"em -v {self.file_dir_path}\{file_name}.son",
            "@echo on"
        ]

class HeaderBlock:
    def __init__(self):
        cur_time = datetime.now()
        self.text = [
            "HEADER",
            f"DAT {cur_time.day}/{cur_time.month}/{cur_time.year} {cur_time.hour}:{cur_time.minute}:{cur_time.second}",
            "BUILT_BY_CREATED NIIMES",
            f"MDATE {cur_time.day}/{cur_time.month}/{cur_time.year} {cur_time.hour}:{cur_time.minute}:{cur_time.second}",
            f"HDATE {cur_time.day}/{cur_time.month}/{cur_time.year} {cur_time.hour}:{cur_time.minute}:{cur_time.second}",
            "EXF",
            "END HEADER"
        ]

class DimensionsBlock:
    def __init__(self):  
        self.text = [
            "DIM",
            "ANG DEG",
            "CAP PF",
            "CON /OH",
            "FREQ GHZ",
            "IND NH",
            "LNG UM",
            "RES OH",
            "END DIM"
        ]

class ControlBlock:
    def __init__(self):
        self.text = [
            "CONTROL",
            "VARSWP",
            "OPTIONS -d",
            "SPEED 1",
            "CACHE_ABS 1",
            "Q_ACC Y",
            "END CONTROL"
        ]

class GeometryBlock:
    def __init__(self, xcell, ycell):
        cell_view = pya.CellView().active()
        self.layout = cell_view.layout()
        self.cell = self.layout.top_cell()
        self.layer_indexes = self.layout.layer_indexes()
        self.x_min = sys.maxsize
        self.y_min = sys.maxsize
        self.x_max = -sys.maxsize
        self.y_max = -sys.maxsize
        self.x_max_sonnet = 0
        self.y_max_sonnet = 0
        self.x_change_sonnet = 0
        self.y_change_sonnet = 0
        self.x_box_size = 0
        self.y_box_size = 0
        self.port_left = False
        self.port_right = False
        self.port_top = False
        self.port_bottom = False
        self.geometry_text = []
        self.ports_text = []
        xcell = float(xcell.replace(',','.'))
        ycell = float(ycell.replace(',','.'))
        self.min_max_coords_on_layout()
        self.max_coords_sonnet()
        self.list_of_ports()
        self.border_size()
        self.list_of_geometry()
        self.text= [
            "GEO",
            "MET \"EM_MET2_Bridge\" 6 TMM 41000000 0.5 5 2",
            "MET \"Met2u\" 4 TMM 41000000 0.5 5.9 2",
            "MET \"Met1u\" 5 TMM 41000000 0.5 0.9 2",
            "MET \"TFR3\" 3 RES 3000",
            "MET \"TFR2\" 2 RES 600",
            "MET \"TFR1\" 1 RES 50",
            "MET \"Met0via\" 2 VOL INF SOLID 0",
            "MET \"BackVia\" 1 VOL 41000000 10",
            f"BOX 5 {self.x_box_size} {self.y_box_size} {math.ceil(self.x_box_size / float(xcell)) * 2} {math.ceil(self.y_box_size / float(ycell)) * 2} 20 0",
            "      500 1 1 0 0 0 0 \"Air\"",
            "      3 2.65 1 0.0008 0 0 0 \"BCB\"",
            "      3.5 2.65 1 0.0008 0 0 0 \"BCB\"",
            "      0.22 7.5 1 0.001 0 0 0 \"SINx\"",
            "      0.22 7.5 1 0.001 0 0 0 \"SINx\"",
            "      85 12.9 1 0.001 0 0 0 \"GaAs\""
        ]
        self.text += self.ports_text + self.geometry_text 
        
    @classmethod        
    def custom_make_translation(self, text, translation) -> str:
        """
        Возвращает строку, в которорой были заменены символы.

        Аргументы:
        - text (str): строка в которой необходимо заменить символы.
        - translation (dict): словарь, в котором хранятся строки которые нужно заменить и на что заменить.

        Возвращает:
        - str: измененная строка.
        """
        regex = re.compile('|'.join(map(re.escape, translation)))
        return regex.sub(lambda match: translation[match.group(0)], text)
    
    def ports_on_layer(self, layer_index: int) -> list:
        """
        Возвращает список объектов типа Text.

        Аргументы:
        - layer_index (int): индекс слоя, на котором будет происходить поиск портов.

        Возвращает:
        - list: список объектов типа Text.
        """
        text_shapes = self.cell.begin_shapes_rec(layer_index)
        ports_array = []

        while not text_shapes.at_end():
            if (str(text_shapes.shape().text) != "None"):
                ports_array.append(text_shapes.shape().text)
            text_shapes.next()

        return ports_array
    
    def region_on_layer(self, layer_index: int) -> pya.Region:
        """
        Возвращает объект типа Region.

        Аргументы:
        - layer_index (int): индекс слоя, из которого будет браться Region.

        Возвращает:
        - Region: Итератор, содержащий один или множество Polygon
        """
        return(pya.Region(self.cell.begin_shapes_rec(layer_index)))
   
    def polygons_in_region(self, region: pya.Region) -> list:
        """
        Возвращает список объектов типа DPolygon.

        Аргументы:
        - region (pya.Region): Итератор, содержащий один или множество Polygon

        Возвращает:
        - list: Список DPolygon, преобразованные в базовые единицы данных (dbu)
        """
        dbu_polygons = []

        for polygon in region:
            dbu_polygons.append(polygon.to_dtype(self.layout.dbu))

        return dbu_polygons

    def points_in_polygon(self, polygon: list) -> list:
        """
        Возвращает список объектов типа list.

        Аргументы:
        - polygon (list): Список, содержащий объекты DPoints

        Возвращает:
        - list: Список точек в полигоне
        """
        points_in_polygon = []
        
        for point in polygon.each_point_hull():
            point_in_polygon = []
            point_in_polygon.append(point.x)
            point_in_polygon.append(point.y)
            points_in_polygon.append(point_in_polygon)

        return points_in_polygon

    def polygons_count(self) -> int:
        """
        Возвращает объект типа int.

        Возвращает:
        - int: Количество полигонов на топологии
        """
        polygons_count = 0

        for i in self.layer_indexes:
            layer_son = self.custom_make_translation(str(str(self.layout.get_info(i)).split()[0]), TRANS_TABLE_LAYERS) 

            if self.layer_filter(layer_son) == True:
                polygons_count += len(self.polygons_in_region(self.region_on_layer(i)))

        return polygons_count

    def min_coords_on_polygon(self, points: list):
        """
        Находит и присваивает минимальные координаты x и y на полигоне:
        - x_min
        - y_min

        Аргументы:
        - points (list): Список, содержащий координаты полигона
        """
        for point in points:
            if point[0] < self.x_min:
                self.x_min = point[0]

            if point[1] < self.y_min:
                self.y_min = point[1]

    def max_coords_on_polygon(self, points: list):
        """
        Находит и присваивает максимальные координаты x и y на полигоне:
        - x_max
        - y_max

        Аргументы:
        - points (list): Список, содержащий координаты полигона
        """
        for point in points:
            if point[0] > self.x_max:
                self.x_max = point[0]

            if point[1] > self.y_max:
                self.y_max = point[1]

    def min_max_coords_on_layout(self):
        """Находит максимальные координаты x и y на топологии"""
        for i in self.layer_indexes:
            layer_son = self.custom_make_translation((str(self.layout.get_info(i)).split()[0]), TRANS_TABLE_LAYERS)
            
            if (self.layer_filter(layer_son) == True):
                polygons = self.polygons_in_region(self.region_on_layer(i))
                for polygon in polygons:
                    points = self.points_in_polygon(polygon)
                    self.min_coords_on_polygon(points)
                    self.max_coords_on_polygon(points)

    def max_coords_sonnet(self):
        """Присваивает x_max_sonnet и y_max_sonnet максимальные координаты, с учетом минимальных координат"""
        if self.x_min <= 0:
            self.x_max_sonnet = self.x_max + abs(self.x_min)
        else:
            self.x_max_sonnet = self.x_max - abs(self.x_min)
        
        if self.y_min <= 0:
            self.y_max_sonnet = self.y_max + abs(self.y_min)
        else:
            self.y_max_sonnet = self.y_max - abs(self.y_min)

    def sonnet_points(self, points: list) -> list:
        """
        Возвращает список точек, подходящих для формата .son

        Аргументы:
        - points (list): Список, содержащий координаты полигона
        Вовращает:
        - list: Список, содержащий координаты x y для Sonnet
        """
        sonnet_points = []
        
        for point in points:
            sonnet_point = []
            if self.x_min <= 0:
                sonnet_point.append(point[0] + abs(self.x_min) + (self.x_change_sonnet - self.x_max_sonnet) / 2)
            else:
                sonnet_point.append(point[0] - abs(self.x_min) + (self.x_change_sonnet - self.x_max_sonnet) / 2)

            if self.y_min <= 0:
                sonnet_point.append(self.y_box_size - (point[1] + abs(self.y_min)) - (self.y_change_sonnet - self.y_max_sonnet) / 2)
            else:
                sonnet_point.append(self.y_box_size - (point[1] - abs(self.y_min)) - (self.y_change_sonnet - self.y_max_sonnet) / 2)
            sonnet_points.append(sonnet_point)

        sonnet_points.append(sonnet_points[0])
        return sonnet_points
    
    def border_size(self):
        """
        Присваивает x_box_size и y_box_size максимальные координаты топологии, с учетом расположения портов. 
        Присваивает x_change_sonnet и y_change_sonnet координаты, на которые нужно сместить топологию.
        """
        if (self.port_left and self.port_right):
            self.x_box_size = self.x_max_sonnet
            self.x_change_sonnet = self.x_max_sonnet

        elif (self.port_left):
            self.x_box_size = self.x_max_sonnet * 1.5
            self.x_change_sonnet = self.x_max_sonnet

        elif (self.port_right):
            self.x_box_size = self.x_max_sonnet * 1.5
            self.x_change_sonnet = self.x_max_sonnet * 2

        else:
            self.x_box_size = self.x_max_sonnet * 2
            self.x_change_sonnet = self.x_max_sonnet * 2

        if (self.port_top and self.port_bottom):
            self.y_box_size = self.y_max_sonnet
            self.y_change_sonnet = self.y_max_sonnet

        elif (self.port_bottom):
            self.y_box_size = self.y_max_sonnet * 1.5
            self.y_change_sonnet = self.y_max_sonnet

        elif (self.port_top):
            self.y_box_size = self.y_max_sonnet * 1.5
            self.y_change_sonnet = self.y_max_sonnet * 2

        else:
            self.y_box_size = self.y_max_sonnet * 2
            self.y_change_sonnet = self.y_max_sonnet * 2    

    def mtype(self, layer) -> int:
        """
        Возвращает mtype для формата .son.

        Возвращает:
        - int: число, которое обозначает материал в Sonnet.
        """
        if layer == 'Met2u':
            return 1
        elif layer == 'Met1u':
            return 2
        elif layer == 'TFR1':
            return 5
        elif layer == 'TFR2':
            return 4
        elif layer == 'TFR3':
            return 3
        elif layer == 'Via2':
            return 7
            
    def ilevel(self, layer) -> int:
        """
        Возвращает ilevel для формата .son.

        Возвращает:
        - int: число, которое обозначает уровень слоя в Sonnet.
        """
        if layer == 'Met2u':
            return 2
        elif (layer == 'Met1u' or layer == 'TFR1' or layer == 'TFR2' or layer == 'TFR3' or layer == 'Via2'):
            return 3
            
    @classmethod        
    def layer_filter(self, layer) -> bool:
        """
        Проверка необходимости переноса слоя в Sonnet.

        Возвращает:
        - bool: флаг, который указывает на необходимость переноса слоя в Sonnet.
        """
        if (layer == 'Met2u' or layer == 'Met1u' or layer == 'TFR1' or layer == 'TFR2' or layer == 'TFR3' or layer == 'Via2'):
            return True  
        else: 
            return False

    def list_of_ports(self):
        """Добавляет в список ports_text информацию о наличии портов на топологии формата .son."""
        polygon_index = 0
        for i in self.layer_indexes:
            layer_son = self.custom_make_translation((str(self.layout.get_info(i)).split()[0]), TRANS_TABLE_LAYERS)

            if (self.layer_filter(layer_son) == True):
                polygons = self.polygons_in_region(self.region_on_layer(i))
                for polygon in polygons:
                    polygon_index += 1
                    for text in self.ports_on_layer(i):
                        port_x = text.x * self.layout.dbu
                        port_y = text.y * self.layout.dbu
                        is_port_vertical = ((port_y == polygon.bbox().bottom or port_y == polygon.bbox().top) and (port_x >= polygon.bbox().left and port_x <= polygon.bbox().right))
                        is_port_lateral = ((port_x == polygon.bbox().left or port_x == polygon.bbox().right) and (port_y >= polygon.bbox().bottom and port_y <= polygon.bbox().top))

                        if (is_port_vertical or is_port_lateral):  
                            self.ports_text.append("POR1 BOX") 
                            self.ports_text.append(f"POLY {polygon_index} 1")
                            
                            if (is_port_vertical and port_y == polygon.bbox().top):
                                self.port_top = True
                                self.ports_text.append("1")
                                
                            elif (is_port_vertical and port_y == polygon.bbox().bottom):
                                self.port_bottom = True
                                self.ports_text.append("3")
                            
                            if (is_port_lateral and port_x == polygon.bbox().left):
                                self.port_left = True
                                self.ports_text.append("0")
                                
                            elif (is_port_lateral and port_x == polygon.bbox().right):
                                self.port_right = True
                                self.ports_text.append("2")

                            self.ports_text.append(f"{text.string} 50 0 0 0 0 0")

    def list_of_geometry(self):
        """Добавляет в список geometry_text информацию о полигонах на топологии формата .son."""
        self.geometry_text.append(f"NUM {self.polygons_count()}")
        polygon_index = 0
        for i in self.layer_indexes:
            layer_son = self.custom_make_translation((str(self.layout.get_info(i)).split()[0]), TRANS_TABLE_LAYERS)

            if (self.layer_filter(layer_son) == True):
                polygons = self.polygons_in_region(self.region_on_layer(i))
                for polygon in polygons:
                    polygon_index += 1 
                    points = self.points_in_polygon(polygon)

                    if (layer_son == 'Via2'):
                        self.geometry_text.append(f"VIA POLYGON")
                        self.geometry_text.append(f"{self.ilevel(layer_son)} {len(points) + 1} {self.mtype(layer_son)} V {polygon_index} 1 1 100 100 0 0 0 Y")
                        self.geometry_text.append(f"TOLEVEL 2 SOLID NOCOVERS")
                        self.geometry_text.append(f"TLAYNAM {layer_son} NOH") 
                    else:
                        self.geometry_text.append(f"{self.ilevel(layer_son)} {len(points) + 1} {self.mtype(layer_son)} V {polygon_index} 1 1 100 100 0 0 0 Y")
                        self.geometry_text.append(f"TLAYNAM {layer_son} INH") 

                    for point in self.sonnet_points(points):
                        self.geometry_text.append(f"{point[0]} {point[1]}")
                    self.geometry_text.append("END")
        
        self.geometry_text.append("END GEO")

class SweepBlock:
    def __init__(self, 
     abs_status, abs_from, abs_to, 
     lin_status, lin_from, lin_to, lin_step):

        self.text = [
          "VARSWP",
          "ENABLED Y",
          "END",
          "END VARSWP"
        ]

        pos = 2
        if abs_status == True:
            str = f"FREQ Y AY ABS_ENTRY {abs_from} {abs_to} -1 300"
            self.text.insert(pos, str)
            pos += 1
        
        if lin_status == True:
            str = f"FREQ Y AN SWEEP {lin_from} {lin_to} {lin_step}"
            self.text.insert(pos, str)

class FileBlock:
    def __init__(self):
        self.number_ports = ports_count()
        self.text = [
            "FILEOUT",
            f"TOUCH D Y $BASENAME.s{self.number_ports}p IC 15 S MA R 50.00000",
            "FOLDER .",
            "END FILEOUT"
        ]

class SonnetProject:
    def __init__(self, file_name,
     abs_status = False, abs_from = 0, abs_to = 0, 
     lin_status = False, lin_from = 0, lin_to = 0, lin_step = 0,
     xcell = 0, ycell = 0):

        self.file_name = file_name

        self.text = [
            "FTYP SONPROJ 18 ! Sonnet Project File",
            "VER 17.56"
        ]
        self.header = HeaderBlock()
        self.dimensions = DimensionsBlock()
        self.control = ControlBlock()
        self.geometry = GeometryBlock(xcell, ycell)
        self.sweep = SweepBlock(abs_status, abs_from, abs_to, lin_status, lin_from, lin_to, lin_step)
        self.file = FileBlock()

        self.params = []
        self.params.append(self.text)
        self.params.append(self.header.text)
        self.params.append(self.dimensions.text)
        self.params.append(self.control.text)
        self.params.append(self.geometry.text)
        self.params.append(self.control.text)
        self.params.append(self.sweep.text)
        self.params.append(self.file.text)

    def create_son_proj(self):
        if os.path.exists(RAW_PATH_TO_KLAYOUT + "\EM") == False:
            os.mkdir(RAW_PATH_TO_KLAYOUT + "\EM")

        cur_dir_path = RAW_PATH_TO_KLAYOUT + rf"\EM\{self.file_name}"

        if os.path.exists(cur_dir_path) == False:
            os.mkdir(cur_dir_path)
            
        Handler.insert_nested_list_to_file(cur_dir_path + f"\{self.file_name}.son", self.params)

def ports_count() -> int:
        """ Функция, которая возращает количество портов на топологии"""
        count = 0
        cv = pya.CellView().active()
        layout = cv.layout()
        cell = layout.top_cell()
        layer_indxs = layout.layer_indexes()
        for i in layer_indxs:
            layer_son = GeometryBlock.custom_make_translation((str(layout.get_info(i)).split()[0]), TRANS_TABLE_LAYERS)

            if (GeometryBlock.layer_filter(layer_son) == True):
                polygons = []
                for polygon in pya.Region(cell.begin_shapes_rec(i)):
                    polygons.append(polygon.to_dtype(layout.dbu))

                text_shapes = cell.begin_shapes_rec(i)
                ports_array = []

                while not text_shapes.at_end():
                    if (str(text_shapes.shape().text) != "None"):
                        ports_array.append(text_shapes.shape().text)
                    text_shapes.next()

                for polygon in polygons:
                    for text in ports_array:
                        port_x = text.x * layout.dbu
                        port_y = text.y * layout.dbu
                        is_port_vertical = ((port_y == polygon.bbox().bottom or port_y == polygon.bbox().top) and (port_x >= polygon.bbox().left and port_x <= polygon.bbox().right))
                        is_port_lateral = ((port_x == polygon.bbox().left or port_x == polygon.bbox().right) and (port_y >= polygon.bbox().bottom and port_y <= polygon.bbox().top))
                        if (is_port_vertical or is_port_lateral):
                            count += 1
        return count