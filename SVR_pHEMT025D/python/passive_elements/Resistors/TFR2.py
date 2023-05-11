import pya 

class TFR2(pya.PCellDeclarationHelper):
    
    def __init__(self):
        
        super(TFR2, self).__init__()
        
        self.tfr2 = pya.LayerInfo(81, 8, "TFR2")
        self.met1 = pya.LayerInfo(91, 10, "Met1")
        
        self.param("tfr2", self.TypeLayer, "Layer of TFR2", default=self.tfr2,hidden=True)
        self.param("met1", self.TypeLayer, "Layer of Met1", default=self.met1,hidden=True)
          
        self.param("width", self.TypeDouble, "Ширина резистора", default=6)
        self.param("length", self.TypeDouble, "Длина резистора", default=8)
        self.param("res", self.TypeDouble, "Сопротивление", readonly=True, unit="Ом")

    def display_text_impl(self):
 
        return (f'SUBCKT | ID=R2 | NET="TFR2" | W={self.width} | L={self.length}')

    def coerce_parameters_impl(self):

        self.res = (self.length / self.width) * 600

        if (self.width < 6  or self.width > 300 ): 
            raise(RuntimeError("Ширина должна быть больше 6 мкм и меньше 300 мкм"))
        
        if(self.length < 8 or self.length > 300):
            raise(RuntimeError("Длинна должна быть больше 8 мкм и меньше 300 мкм"))

    def produce_impl(self):
  
        self.cell.shapes(self.met1_layer).insert(pya.Box(0, 0, 6000, self.width*1000+2000))
        self.cell.shapes(self.met1_layer).insert(pya.Box(self.length*1000 +6000, 0, self.length*1000+12000, self.width*1000+2000))
        self.cell.shapes(self.tfr2_layer).insert(pya.Box(2000, 1000, self.length*1000+10000, self.width*1000+1000))