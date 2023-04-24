import pya

class BRIDGE(pya.PCellDeclarationHelper):

  def __init__(self):

    super(BRIDGE, self).__init__()
    
    self.met1 = pya.LayerInfo(91, 10, "Met1")
    self.met2 = pya.LayerInfo(92, 13, "Met2")
    self.via2 = pya.LayerInfo(71, 11, "Via2")
    self.via3 = pya.LayerInfo(72, 12, "Via3")
    
    self.param("met1", self.TypeLayer, "Layer of met1", default=self.met1, hidden=True)
    self.param("met2", self.TypeLayer, "Layer of met1", default=self.met2, hidden=True)
    self.param("via2", self.TypeLayer, "Layer of via2", default=self.via2, hidden=True)
    self.param("via3", self.TypeLayer, "Layer of via3", default=self.via3, hidden=True)
    
    self.param("w1", self.TypeInt, "Ширина первого и третьего выходов", default=10)
    self.param("w2", self.TypeInt, "Ширина второго и четвертого выходов", default=10)
      
  def display_text_impl(self):
  
    return (f'SUBCKT | ID=S1 | NET="BRIDGE" | w12={self.w1} | w24={self.w2}')
    
  def coerce_parameters_impl(self):

        if (self.w1 < 10  or self.w1 > 50 ): 
            raise(RuntimeError("Ширина w1 должна быть больше 10 мкм и меньше 50 мкм"))
        
        if (self.w2 < 10 or self.w2 > 50):
            raise(RuntimeError("Ширина w2 должна быть больше 10 мкм и меньше 50 мкм"))  
              
  def produce_impl(self):
                
        self.cell.shapes(self.met1_layer).insert(pya.Box(17000,500, 17000+self.w2*1000, 8500))
        self.cell.shapes(self.met1_layer).insert(pya.Box(17000,self.w1*1000+28500, 17000+self.w2*1000, self.w1*1000+36500))
        self.cell.shapes(self.via2_layer).insert(pya.Box(19000,2500, 15000+self.w2*1000, 6500))
        self.cell.shapes(self.via2_layer).insert(pya.Box(19000,self.w1*1000+30500, 15000+self.w2*1000, self.w1*1000+34500))
        self.cell.shapes(self.via3_layer).insert(pya.Box(16500,0, 17500+self.w2*1000, 9000))
        self.cell.shapes(self.via3_layer).insert(pya.Box(16500,self.w1*1000+28000, 17500+self.w2*1000, self.w1*1000+37000))
        self.cell.shapes(self.met2_layer).insert(pya.Box(18000,1500, 16000+self.w2*1000, self.w1*1000+35500))
        self.cell.shapes(self.met2_layer).insert(pya.Box(18000,6500, 16000+self.w2*1000, 7500))
        self.cell.shapes(self.met2_layer).insert(pya.Box(18000,self.w1*1000+29500, 16000+self.w2*1000, self.w1*1000+30500))
        self.cell.shapes(self.met1_layer).insert(pya.Box(0, 18500, self.w2*1000+34000, self.w1*1000+18500))
        self.cell.shapes(self.met1_layer).insert(pya.Box(0, 17500+self.w1*1000/2, 2000, 19500+self.w1*1000/2))
        self.cell.shapes(self.met1_layer).insert(pya.Box(7000,18500, 8000, self.w1*1000+18500))  
        self.cell.shapes(self.met1_layer).insert(pya.Box(26000+self.w2*1000,18500, 27000+self.w2*1000, self.w1*1000+18500))
        self.cell.shapes(self.via2_layer).insert(pya.Box(2000,20500, 6000, self.w1*1000+16500))
        self.cell.shapes(self.via2_layer).insert(pya.Box(28000+self.w2*1000,20500, 32000+self.w2*1000, self.w1*1000+16500))
        self.cell.shapes(self.via3_layer).insert(pya.Box(-500,18000, 8500, self.w1*1000+19000))
        self.cell.shapes(self.via3_layer).insert(pya.Box(25500+self.w2*1000,18000, 34500+self.w2*1000, self.w1*1000+19000))
        self.cell.shapes(self.met2_layer).insert(pya.Box(1000,19500, 7000, self.w1*1000+17500))
        self.cell.shapes(self.met2_layer).insert(pya.Box(27000+self.w2*1000,19500, 33000+self.w2*1000, self.w1*1000+17500))