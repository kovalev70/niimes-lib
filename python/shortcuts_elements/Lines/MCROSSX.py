import pya

class MCROSSX(pya.PCellDeclarationHelper):

  def __init__(self):

    super(MCROSSX, self).__init__()
    
    self.met1 = pya.LayerInfo(91, 10, "Met1")
    self.met2 = pya.LayerInfo(92, 13, "Met2")
    self.via2 = pya.LayerInfo(71, 11, "Via2")
    self.via3 = pya.LayerInfo(72, 12, "Via3")
    
    self.param("met1", self.TypeLayer, "Layer of met1", default=self.met1, hidden=True)
    self.param("met2", self.TypeLayer, "Layer of met1", default=self.met2, hidden=True)
    self.param("via2", self.TypeLayer, "Layer of via2", default=self.via2, hidden=True)
    self.param("via3", self.TypeLayer, "Layer of via3", default=self.via3, hidden=True)
    
    self.param("w2", self.TypeInt, "Ширина второго и четвертого выходов", default=20)
    self.param("w1", self.TypeInt, "Ширина первого и третьего выхода", default=15)
    self.param("Met1", self.TypeBoolean, "Линия выполнена в Met1", default=True)
    self.param("Met2", self.TypeBoolean, "Линия выполнена в Met2", default=True)
      
  def display_text_impl(self):
  
    return (f'SUBCKT | ID=MX1 | NET="MCROSSX" | w1={self.w1} | w2={self.w2}')

  def coerce_parameters_impl(self):
            
    if (self.Met1 == False and self.Met2 == False):
        raise(RuntimeError("Необходимо выбрать металл"))

  def produce_impl(self):

    pts_via2 = [pya.Point(0,4000), pya.Point(0, self.w1*1000),pya.Point(4000, self.w1*1000),
                pya.Point(4000,self.w1*1000+4000),pya.Point(self.w2*1000, self.w1*1000+4000),
                pya.Point(self.w2*1000, self.w1*1000),pya.Point(self.w2*1000+4000, self.w1*1000),
                pya.Point(self.w2*1000+4000, 4000), pya.Point(self.w2*1000, 4000),pya.Point(self.w2*1000, 0),
                pya.Point(4000, 0),pya.Point(4000, 4000),]
                
    pts_met2 = [pya.Point(1000,3000), pya.Point(1000, self.w1*1000+1000),pya.Point(3000, self.w1*1000+1000),
                pya.Point(3000,self.w1*1000+3000),pya.Point(self.w2*1000+1000, self.w1*1000+3000),
                pya.Point(self.w2*1000+1000, self.w1*1000+1000),pya.Point(self.w2*1000+3000, self.w1*1000+1000),
                pya.Point(self.w2*1000+3000, 3000), pya.Point(self.w2*1000+1000, 3000),pya.Point(self.w2*1000+1000, 1000),
                pya.Point(3000, 1000),pya.Point(3000, 3000),]
                
    self.cell.shapes(self.via2_layer).insert(pya.Polygon(pts_via2))
    self.cell.shapes(self.via3_layer).insert(pya.Box(1500,1500, self.w2*1000+2500, self.w1*1000+2500))
    
    if (self.Met2 == True):
        self.cell.shapes(self.met2_layer).insert(pya.Polygon(pts_met2))
        
    if (self.Met1 == True):
        self.cell.shapes(self.met1_layer).insert(pya.Box(2000,2000, self.w2*1000+2000, self.w1*1000+2000))