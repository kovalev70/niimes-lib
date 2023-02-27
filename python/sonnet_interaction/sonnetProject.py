from datetime import datetime
import os
import re
import sys
import pya
import math

RAW_PATH_TO_KLAYOUT = r"{}".format(os.getcwd())

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
            "mode con:cols=67 lines=10",
            rf"cd {path_to_sonnet}",
            "ECHO #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#",
            "ECHO #             Simulation will start now, please wait..            #",
            "ECHO #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#",
            rf"em {self.file_dir_path}\{file_name}.son",
            "TIMEOUT /T 20 /NOBREAK",
            "EXIT"
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
        self.x_min = sys.maxsize
        self.y_min = sys.maxsize
        self.box = self.box_size()
        xcell = float(xcell.replace(',','.'))
        ycell = float(ycell.replace(',','.'))
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
            f"BOX 5 {self.box[0]} {math.ceil(self.box[1]*1.5)} {int(self.box[0] / xcell) * 2} {math.ceil(math.ceil(self.box[1]*1.5) / float(ycell)) * 2} 20 0",
            "      500 1 1 0 0 0 0 \"Air\"",
            "      3 2.65 1 0.0008 0 0 0 \"BCB\"",
            "      3.5 2.65 1 0.0008 0 0 0 \"BCB\"",
            "      0.22 7.5 1 0.001 0 0 0 \"SINx\"",
            "      0.22 7.5 1 0.001 0 0 0 \"SINx\"",
            "      85 12.9 1 0.001 0 0 0 \"GaAs\""
        ]
        self.creating_geometry() 
           
    def custom_make_translation(self, text, translation):
        regex = re.compile('|'.join(map(re.escape, translation)))
        return regex.sub(lambda match: translation[match.group(0)], text)
    
    def box_size(self):
        cv = pya.CellView().active()
        ly = cv.layout()
        x_max = 0
        y_max = 0
        box = []
        for cell in ly.each_cell():
           for i in range(0, ly.layers()):
              shapes = cell.shapes(i)
              region = pya.Region(shapes)
              trans_table_layers = {'Met1': 'Met1u', 'Met2':'Met2u', '80/7': 'TFR1', '81/8': 'TFR2',
                                  '82/9': 'TFR3', '91/10': 'Met1u', '71/11': 'Via2', '92/13': 'Met2u'}
              layer_info = str(ly.get_info(i)).split()
              layer_son = self.custom_make_translation(str(layer_info[0]), trans_table_layers)
              
              if((len(str(region)) > 0) and (self.layer_filter(layer_son) == True)):
                    trans_table_r = {');': None, '(': None, ',': ' ', ';': ' ', ')': None}
                    r =[]
                    
                    for i in region:
                        r.append(self.custom_make_translation(str(i), trans_table_r))
                        
                    for j in range(0, len(r)):
                        points_count = 2 * (((len(re.findall(" ",r[j])))//2) + 1)
                        point = []
                        point = r[j].split(' ')
                        
                        for l in range(0, points_count):
                            x = sys.maxsize
                            y = sys.maxsize
                            if(l % 2 == 0):   
                                x = float(point[l]) * ly.dbu 
                            else:
                                y = ly.dbu * (float(point[l]))
                            if(x < self.x_min):
                                self.x_min = x
                            if(y < self.y_min):
                                self.y_min = y
                                
           for i in range(0, ly.layers()):
              shapes = cell.shapes(i)
              region = pya.Region(shapes)
              trans_table_layers = {'Met1': 'Met1u', 'Met2':'Met2u', '80/7': 'TFR1', '81/8': 'TFR2',
                                  '82/9': 'TFR3', '91/10': 'Met1u', '71/11': 'Via2', '92/13': 'Met2u'}
              layer_info = str(ly.get_info(i)).split()
              layer_son = self.custom_make_translation(str(layer_info[0]), trans_table_layers)
              
              if((len(str(region)) > 0) and (self.layer_filter(layer_son) == True)):
                  trans_table_r = {');': None, '(': None, ',': ' ', ';': ' ', ')': None}
                  r =[]
                    
                  for i in region:
                      r.append(self.custom_make_translation(str(i), trans_table_r))
                      
                      x = 0
                      y = 0
                        
                      for j in range(0, len(r)):
                          points_count= 2 * (((len(re.findall(" ",r[j])))//2) + 1)
                          point = []
                          point = r[j].split(' ')
  
                          for l in range(0, points_count):
                              if(l % 2 == 0):
                                  if(self.x_min < 0):
                                      x = float(point[l]) * ly.dbu + abs(self.x_min)
                                  else:
                                      x = float(point[l]) * ly.dbu - abs(self.x_min)
                              else:
                                  if(self.y_min < 0):
                                      y = ly.dbu * (float(point[l])) + abs(self.y_min)
                                  else:
                                      y = ly.dbu * (float(point[l])) - abs(self.y_min)
                              if (x > x_max):
                                  x_max = x
                                  
                              if (y > y_max):
                                  y_max = y
                            
        box = [x_max, y_max]       
        return box
        
    def mtype(self, layer):
        if (layer == 'Met2u'):
            return 1
        elif (layer == 'Met1u'):
            return 2
        elif (layer == 'TFR1'):
            return 5
        elif (layer == 'TFR2'):
            return 4
        elif (layer == 'TFR3'):
            return 3
        elif (layer == 'Via2' or layer == 'Via3' or layer == 'BackVia'):
            return 7
            
    def ilevel(self, layer):
        if (layer == 'Met2u'):
            return 2
        elif (layer == 'Met1u'):
            return 3
        elif (layer == 'TFR1'):
            return 3
        elif (layer == 'TFR2'):
            return 3
        elif (layer == 'TFR3'):
            return 3
        elif (layer == 'Via2'):
            return 3
            
    def layer_filter(self, layer):
        if (layer == 'Met2u' or layer == 'Met1u' or layer == 'TFR1' or layer == 'TFR2' or layer == 'TFR3' or layer == 'Via2'):
            return True  
        else: 
            return False
            
    def ports(self, layer_index, cell, layout, polygon_index):
        si = layout.cell(cell.name).begin_shapes_rec(layer_index)
        x_coords_left = []
        x_coords_right = []
        y_coords_bottom = []
        y_coords_top = []
        count_polygon = 0
        while not si.at_end():
            iPolygon = polygon_index 
            text = si.shape().text
            bbox = si.shape().bbox().transformed(si.trans())
            
            if (str(text) == 'None'):
                count_polygon += 1
                x_coords_left.append(bbox.left)
                x_coords_right.append(bbox.right)
                y_coords_bottom.append(bbox.bottom)
                y_coords_top.append(bbox.top)
            else:
                for i in range(0, count_polygon):
                    iPolygon += 1
                    is_port_vertical = ((text.y == y_coords_bottom[i] or text.y == y_coords_top[i]) and (text.x >= x_coords_left[i] and text.x <= x_coords_right[i]))
                    is_port_lateral = ((text.x == x_coords_left[i] or text.x == x_coords_right[i]) and (text.y >= y_coords_bottom[i] and text.y <= y_coords_top[i]))

                    if (is_port_lateral or is_port_vertical):
                        if (float(self.x_min) < 0):
                            x = float(text.x) * layout.dbu + abs(self.x_min)
                        else:
                            x = float(text.x) * layout.dbu - abs(self.x_min)
                            
                        if(float(self.y_min) < 0):
                            y = math.ceil(1.5 * self.box[1]) - (layout.dbu * (float(text.y)) + abs(self.y_min)) - (math.ceil(1.5* self.box[1]) - self.box[1])/2
                        else:
                            y = math.ceil(1.5 * self.box[1]) - (layout.dbu * (float(text.y)) - abs(self.y_min)) - (math.ceil(1.5* self.box[1]) - self.box[1])/2
                            
                        self.text.append("POR1 BOX") 
                        self.text.append(f"POLY {iPolygon} 1")
                        
                        if(is_port_vertical and text.y == y_coords_top[i]):
                            self.text.append("1")
                            
                        elif(is_port_vertical and text.y == y_coords_bottom[i]):
                            self.text.append("3")
                        
                        if(is_port_lateral and text.x == x_coords_left[i]):
                            self.text.append("0")
                            
                        elif(is_port_lateral and text.x == x_coords_right[i]):
                            self.text.append("2")
                        
                        self.text.append(f"{text.string} 50 0 0 0 {x} {y} ")
                
            si.next()
        
    def creating_geometry(self):
        exception_num = 0
        if(self.box[1] <= 1.5):
            exception_num = 0.25 
            
        cv = pya.CellView().active()
        ly = cv.layout()
        num = 0
        trans_table_layers = {'Met1': 'Met1u', 'Met2':'Met2u', '80/7': 'TFR1', '81/8': 'TFR2',
                                  '82/9': 'TFR3', '91/10': 'Met1u', '71/11': 'Via2', '92/13': 'Met2u'}
        for cell in ly.each_cell():
            for i in range(0, ly.layers()):
                shapes = cell.shapes(i)
                region = pya.Region(shapes)
                layer_info = str(ly.get_info(i)).split()
                layer_son = self.custom_make_translation(str(layer_info[0]), trans_table_layers)
                
                if((len(str(region)) > 0) and (self.layer_filter(layer_son) == True)):
                    self.ports(i, cell, ly, num)
                    num += len(region)
                
        if(num > 0):
            self.text.append(f"NUM {str(num)}")
        
        for cell in ly.each_cell():
           polygon_index = 0
           
           for i in range(0, ly.layers()):
              shapes = cell.shapes(i)
              region = pya.Region(shapes)
              layer_info = str(ly.get_info(i)).split()
              layer_son = self.custom_make_translation(str(layer_info[0]), trans_table_layers)

              if((len(str(region)) > 0) and (self.layer_filter(layer_son) == True)):
                    trans_table_r = {');': None, '(': None, ',': ' ', ';': ' ', ')': None}
                    r =[]
                    for i in region:
                        r.append(self.custom_make_translation(str(i), trans_table_r))
                        
                    for j in range(0, len(region)):
                        polygon_index += 1
                        points_count= ((len(re.findall(" ",r[j])))//2) + 2
                        toLevel = 0
                        point = []
                        point = r[j].split(' ')
                        if(layer_son == 'Via2'):
                            toLevel = 2
                            self.text.append("VIA POLYGON")    
                            
                        self.text.append(f"{self.ilevel(layer_son)} {points_count} {self.mtype(layer_son)} V {polygon_index} 1 1 100 100 0 0 0 Y")
                        
                        if(layer_son == 'Via2'):
                            self.text.append(f"TOLEVEL {toLevel} SOLID NOCOVERS")
                            self.text.append(f"TLAYNAM {layer_son} NOH") 
                        else:
                            self.text.append(f"TLAYNAM {layer_son} INH")    
                             
                        for l in range(0, points_count*2 - 2, 2):
                            for n in range(0, 2):
                                if(n == 0):

                                    if (float(self.x_min) < 0):
                                        x = float(point[l+n]) * ly.dbu + abs(self.x_min)
                                    else:
                                        x = float(point[l+n]) * ly.dbu - abs(self.x_min)
                                else:

                                    if(float(self.y_min) < 0):
                                        y = math.ceil(1.5 * self.box[1]) - (ly.dbu * (float(point[l+n])) + abs(self.y_min)) - (math.ceil(1.5* self.box[1]) - self.box[1])/2
                                    else:
                                        y = math.ceil(1.5 * self.box[1]) - (ly.dbu * (float(point[l+n])) - abs(self.y_min)) - (math.ceil(1.5* self.box[1]) - self.box[1])/2          
                            self.text.append(f"{x} {y}")
                            
                            if(l == (points_count*2 - 4)):
                                if (float(self.x_min) < 0):
                                    x = float(point[0]) * ly.dbu + abs(self.x_min)
                                else:
                                    x = float(point[0]) * ly.dbu - abs(self.x_min)
                                    
                                if(float(self.y_min) < 0):
                                    y = math.ceil(1.5 * self.box[1]) - (ly.dbu * (float(point[l+n])) + abs(self.y_min)) - (math.ceil(1.5* self.box[1]) - self.box[1])/2
                                else:
                                    y = math.ceil(1.5 * self.box[1]) - (ly.dbu * (float(point[l+n])) - abs(self.y_min)) - (math.ceil(1.5* self.box[1]) - self.box[1])/2
  
                                self.text.append(f"{x} {y}") 
                                        
                        self.text.append("END")             
        self.text.append("END GEO")

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
        self.number_ports = self.__ports_count()
        self.text = [
            "FILEOUT",
            f"TOUCH D Y $BASENAME.s{self.number_ports}p IC 15 S MA R 50.00000",
            "FOLDER .",
            "END FILEOUT"
        ]

    def __ports_count(self):
        count = 0
        cv = pya.CellView().active()
        ly = cv.layout()
            
        for cell in ly.each_cell():
            for i in range(0, ly.layers()):
                shapes = cell.shapes(i)
                r = pya.Region(shapes)
                if(len(str(r)) > 0):
                    si = ly.cell(cell.name).begin_shapes_rec(i)
                            
                    while not si.at_end():
                        text = si.shape().text
                                
                        if (str(text) != 'None'):
                            count += 1
                                    
                        si.next()
                            
        return count

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

