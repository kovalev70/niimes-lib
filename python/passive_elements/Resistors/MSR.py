import pya 

class MSR(pya.PCellDeclarationHelper):
    
    def __init__(self):
        
        super(MSR, self).__init__()
        
        self.mesa = pya.LayerInfo(40, 2, "Mesa")
        self.ohmic = pya.LayerInfo(20, 1, "Ohmic")
        self.via1 = pya.LayerInfo(70, 6, "Via1")
        self.met1 = pya.LayerInfo(91, 10, "Met1")
        
        self.param("mesa", self.TypeLayer, "Layer of Mesa", default=self.mesa, hidden=True)
        self.param("ohmic", self.TypeLayer, "Layer of Ohmic", default=self.ohmic, hidden=True)
        self.param("via1", self.TypeLayer, "Layer of Via1", default=self.via1, hidden=True)
        self.param("met1", self.TypeLayer, "Layer of Met1", default=self.met1, hidden=True)
          
        self.param("width", self.TypeDouble, "Ширина резистора", default=10)
        self.param("length", self.TypeDouble, "Длина резистора", default=10)
        
    def display_text_impl(self):

        return (f'SUBCKT | ID=R4 | NET="MSR" | W={self.width} | L={self.length}')

    def coerce_parameters_impl(self):

        if (self.width < 10  or self.width > 300 ): 
            raise(RuntimeError("Ширина должна быть больше 10 мкм и меньше 300 мкм"))
        
        if(self.length < 10 or self.length > 300):
            raise(RuntimeError("Длина должна быть больше 10 мкм и меньше 300 мкм"))
      
    def produce_impl(self):
        
        pts_mesa = [pya.Point(0,0),pya.Point(0,self.width*1000+2000),pya.Point(10000,self.width*1000+2000),
                    pya.Point(10000,self.width*1000+1000),pya.Point(1000*self.length+8000,self.width*1000+1000),pya.Point(1000*self.length+8000,self.width*1000+2000),
                    pya.Point(1000*self.length+18000,self.width*1000+2000),pya.Point(1000*self.length+18000,0),pya.Point(1000*self.length+8000,0),
                    pya.Point(1000*self.length+8000,1000),pya.Point(10000,1000),pya.Point(10000,0)]
        
        self.cell.shapes(self.mesa_layer).insert(pya.Polygon(pts_mesa))
        self.cell.shapes(self.ohmic_layer).insert(pya.Box(1000,1000,9000,self.width*1000+1000))
        self.cell.shapes(self.ohmic_layer).insert(pya.Box(self.length*1000+9000,1000,self.length*1000+17000,self.width*1000+1000))
        
        self.cell.shapes(self.met1_layer).insert(pya.Box(2000,2000,8000,self.width*1000))
        self.cell.shapes(self.met1_layer).insert(pya.Box(self.length*1000+10000,2000,self.length*1000+16000,self.width*1000))
        
        self.cell.shapes(self.via1_layer).insert(pya.Box(2500,2500,7500,self.width*1000-500))
        self.cell.shapes(self.via1_layer).insert(pya.Box(self.length*1000+10500, 2500, self.length*1000+15500, self.width*1000-500))