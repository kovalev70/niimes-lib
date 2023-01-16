import pya 

class MLIN(pya.PCellDeclarationHelper):
    
    def __init__(self):
        
        super(MLIN, self).__init__()
        
        self.via2 = pya.LayerInfo(71, 11, "Via2")
        self.via3 = pya.LayerInfo(72, 12, "Via3")
        self.met1 = pya.LayerInfo(91, 10, "Met1")
        self.met2 = pya.LayerInfo(92, 13, "Met2")

        self.param("via2", self.TypeLayer, "Layer of Via2", default=self.via2, hidden=True)
        self.param("via3", self.TypeLayer, "Layer of Via3", default=self.via3, hidden=True)
        self.param("met1", self.TypeLayer, "Layer of Met1", default=self.met1, hidden=True)
        self.param("met2", self.TypeLayer, "Layer of Met2", default=self.met2, hidden=True)
        
        self.param("L", self.TypeDouble, "Длина линии", default=100)
        self.param("W", self.TypeDouble, "Ширина линии", default=20)

        self.param("left_point", self.TypeShape, "", default = pya.DPoint(0, 0))
        self.param("right_point", self.TypeShape, "", default = pya.DPoint(0, 0))
        self.param("Met1", self.TypeBoolean, "Линия выполнена в Met1", default=True)
        self.param("Met2", self.TypeBoolean, "Линия выполнена в Met2", default=True)

        self.param("flag", self.TypeBoolean, "", default=True, hidden=True)
        self.param("l_buf", self.TypeDouble, "", default=0, hidden=True)
        self.param("sum_x", self.TypeDouble, "", default=0, hidden=True)

    def display_text_impl(self):

        return (f'MLIN | ID=TL1 | L={self.L} | W={self.W}')

    def coerce_parameters_impl(self):

        if (self.Met1 == False and self.Met2 == False):
            raise(RuntimeError("Необходимо выбрать металл"))

        if self.flag:
            self.left_point.x = -(self.L / 2 + 0.5)
            self.right_point.x = (self.L / 2 + 0.5)
            self.flag = False

        if (abs(self.left_point.x) != self.right_point.x) and self.sum_x != (self.left_point.x + self.right_point.x):
            if self.left_point.x < 0 and self.right_point.x > 0:
                self.L = round((abs(self.left_point.x) + abs(self.right_point.x) - 1), 1)
            elif self.left_point.x > 0:
                self.L = round((self.right_point.x - self.left_point.x - 1), 1)
            elif self.right_point.x < 0:
                self.L = round((abs(self.left_point.x) - abs(self.right_point.x) - 1), 1)
            
            self.l_buf = self.L
            self.sum_x = self.left_point.x + self.right_point.x

        else:
            if self.l_buf != self.L:
                self.left_point.x = -(self.L / 2 + 0.5)
                self.right_point.x = (self.L / 2 + 0.5)

        self.left_point.y = 0
        self.right_point.y = 0        

    def produce_impl(self):
        
        if self.Met1 and self.Met2:
            self.cell.shapes(self.via2_layer).insert(pya.Box(pya.Point((self.left_point.x + 2.5) * 1000, (self.W / 2 - 2) * 1000), pya.Point((self.right_point.x - 2.5) * 1000, -(self.W / 2 - 2) * 1000)))
            self.cell.shapes(self.via3_layer).insert(pya.Box(pya.Point((self.left_point.x) * 1000, (self.W / 2 + 0.5) * 1000), pya.Point((self.right_point.x) * 1000, -(self.W / 2 + 0.5) * 1000)))

        if self.Met1:
            self.cell.shapes(self.met1_layer).insert(pya.Box(pya.Point((self.left_point.x + 0.5) * 1000, (self.W / 2) * 1000), pya.Point((self.right_point.x - 0.5) * 1000, -(self.W / 2) * 1000)))

        if self.Met2:
            if self.Met1 == False:
                self.cell.shapes(self.met2_layer).insert(pya.Box(pya.Point((self.left_point.x + 0.5) * 1000, (self.W / 2) * 1000), pya.Point((self.right_point.x - 0.5) * 1000, -(self.W / 2) * 1000)))
            else:
                self.cell.shapes(self.met2_layer).insert(pya.Box(pya.Point((self.left_point.x + 1.5) * 1000, (self.W / 2 - 1) * 1000), pya.Point((self.right_point.x - 1.5) * 1000, -(self.W / 2 - 1) * 1000)))
