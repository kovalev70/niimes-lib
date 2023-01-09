import pya 

class MIMCAP1(pya.PCellDeclarationHelper):
    
  def __init__(self):
  
    super(MIMCAP1, self).__init__()
        
    self.met1 = pya.LayerInfo(91, 10, "Met1")
    self.met2 = pya.LayerInfo(92, 13, "Met2")
    self.via2 = pya.LayerInfo(71, 11, "Via2")
    self.via3 = pya.LayerInfo(72, 12, "Via3")
        
    self.param("met1", self.TypeLayer, "Layer of Met1", default=self.met1, hidden = True)
    self.param("met2", self.TypeLayer, "Layer of Met2", default=self.met2, hidden = True)
    self.param("via2", self.TypeLayer, "Layer of Via2", default=self.via2, hidden = True)  
    self.param("via3", self.TypeLayer, "Layer of Via3", default=self.via3, hidden = True) 

    self.param("width", self.TypeDouble, "Ширина конденсатора", default=30)
    self.param("length", self.TypeDouble, "Длина конденсатора", default=30)
    self.param("w1", self.TypeDouble, "Ширина подводящего проводника", default=12)
    self.param("outMet2", self.TypeBoolean, "Выход с met1", default=True)
    self.param("outMet1", self.TypeBoolean, "Выход с met2", default=True)
        
  def display_text_impl(self):

    return (f'SUBCKT | ID=C1 | NET="MIMCAP1 | W={self.width} | L={self.length} | W1={self.w1}')
    
  def coerce_parameters_impl(self):

    if (self.width < 20  or self.width > 450 ): 
        raise(RuntimeError("Ширина конденсатора должна быть больше 20 и меньше 450"))
        
    if(self.length < 20 or self.length > 450):
        raise(RuntimeError("Длина конденсатора должна быть болшьше 20 и меньше 450"))
            
    if(self.w1 < 12 or self.length > 150):
        raise(RuntimeError("Ширина подводящего проводника должна быть болшьше 12 и меньше 150"))

  def produce_impl(self):
    
    self.cell.shapes(self.met1_layer).insert(pya.Box(0,(self.width*1000+6000-self.w1*1000)/2,17000,(self.width*1000+6000+self.w1*1000)/2))
    self.cell.shapes(self.met1_layer).insert(pya.Box(0,(self.width*1000+16000-self.w1*1000)/2,2000,(self.width*1000- 4000+self.w1*1000)/2))
    self.cell.shapes(self.met1_layer).insert(pya.Box(17000,0,23000+1000*self.length,self.width*1000+6000))
    self.cell.shapes(self.via3_layer).insert(pya.Box(20000,3000,20000+1000*self.length,self.width*1000+3000))

    self.cell.shapes(self.met2_layer).insert(pya.Box(22000+1000*self.length,(self.width*1000+8000-self.w1*1000)/2,41000+1000*self.length,(self.width*1000+4000+self.w1*1000)/2))
    self.cell.shapes(self.met2_layer).insert(pya.Box(18000,1000,22000+1000*self.length,self.width*1000+5000))
        
    if self.outMet1 == True:
        self.cell.shapes(self.met1_layer).insert(pya.Box(33000+1000*self.length,(self.width*1000+6000-self.w1*1000)/2,42000+1000*self.length,(self.width*1000+6000+self.w1*1000)/2))
        self.cell.shapes(self.met1_layer).insert(pya.Box(40000+1000*self.length,(self.width*1000+16000-self.w1*1000)/2,42000+1000*self.length,(self.width*1000- 4000+self.w1*1000)/2))
        self.cell.shapes(self.via2_layer).insert(pya.Box(35000+1000*self.length,(self.width*1000+10000-self.w1*1000)/2,40000+1000*self.length,(self.width*1000+2000+self.w1*1000)/2))
        self.cell.shapes(self.via3_layer).insert(pya.Box(32500+1000*self.length,(self.width*1000+5000-self.w1*1000)/2,42500+1000*self.length,(self.width*1000+7000+self.w1*1000)/2))
    if self.outMet2 == True:
        self.cell.shapes(self.met2_layer).insert(pya.Box(1000,(self.width*1000+8000-self.w1*1000)/2,8000,(self.width*1000+4000+self.w1*1000)/2))
        self.cell.shapes(self.via2_layer).insert(pya.Box(2000,(self.width*1000+10000-self.w1*1000)/2,7000,(self.width*1000+2000+self.w1*1000)/2))
        self.cell.shapes(self.via3_layer).insert(pya.Box(-500,(self.width*1000+5000-self.w1*1000)/2,9500,(self.width*1000+7000+self.w1*1000)/2))