import pya 

class MIMCAP2(pya.PCellDeclarationHelper):
    
  def __init__(self):
  
    super(MIMCAP2, self).__init__()
    
    self.met0 = pya.LayerInfo(90, 5, "Met0")
    self.met1 = pya.LayerInfo(91, 10, "Met1")
    self.met2 = pya.LayerInfo(92, 13, "Met2")
    self.via1 = pya.LayerInfo(70, 6, "Via1")
    self.via2 = pya.LayerInfo(71, 11, "Via2")
    self.via3 = pya.LayerInfo(72, 12, "Via3")
        
    self.param("met1", self.TypeLayer, "Layer of Met1", default=self.met1, hidden = True)
    self.param("met2", self.TypeLayer, "Layer of Met2", default=self.met2, hidden = True)
    self.param("via2", self.TypeLayer, "Layer of Via2", default=self.via2, hidden = True)  
    self.param("via3", self.TypeLayer, "Layer of Via3", default=self.via3, hidden = True) 
    self.param("via1", self.TypeLayer, "Layer of Via1", default=self.via1, hidden = True)
    self.param("met0", self.TypeLayer, "Layer of Met0", default=self.met0, hidden = True) 

    self.param("width", self.TypeDouble, "Ширина конденсатора", default=30)
    self.param("length", self.TypeDouble, "Длина конденсатора", default=30)
    self.param("w1", self.TypeDouble, "Ширина подводящего проводника", default=12)
    self.param("outMet2", self.TypeBoolean, "Выход с met0", default=True)
    self.param("outMet1", self.TypeBoolean, "Выход с met2", default=True)
        
  def display_text_impl(self):

    return (f'SUBCKT | ID=C1 | NET="MIMCAP2 | W={self.width} | L={self.length} | W1={self.w1}')
    
  def coerce_parameters_impl(self):

    if (self.width < 20  or self.width > 150 ): 
        raise(RuntimeError("Ширина конденсатора должна быть больше 20 и меньше 450"))
        
    if(self.length < 20 or self.length > 150):
        raise(RuntimeError("Длина конденсатора должна быть болшьше 20 и меньше 450"))
            
    if(self.w1 < 12 or self.w1 > 50):
        raise(RuntimeError("Ширина подводящего проводника должна быть болшьше 12 и меньше 150"))

  def produce_impl(self):
    
    self.cell.shapes(self.met0_layer).insert(pya.Box(0,(self.width*1000+2000-self.w1*1000)/2,19000,(self.width*1000+6000+self.w1*1000)/2))
    self.cell.shapes(self.met0_layer).insert(pya.Box(19000,0,23000+1000*self.length,self.width*1000+4000))
    self.cell.shapes(self.via3_layer).insert(pya.Box(23500,4500,18500+1000*self.length,self.width*1000-500))
    self.cell.shapes(self.met1_layer).insert(pya.Box(21000,2000,21000+1000*self.length,self.width*1000+2000))    
    self.cell.shapes(self.met2_layer).insert(pya.Box(19500+1000*self.length,(self.width*1000+6000-self.w1*1000)/2,41500+1000*self.length,(self.width*1000+2000+self.w1*1000)/2))
    self.cell.shapes(self.met2_layer).insert(pya.Box(22500,3500,19500+1000*self.length,self.width*1000+500))
    self.cell.shapes(self.via2_layer).insert(pya.Box(24500,5500,17500+1000*self.length,self.width*1000-1500))
        
    if self.outMet1 == True:
        self.cell.shapes(self.met1_layer).insert(pya.Box(33500+1000*self.length,(self.width*1000+4000-self.w1*1000)/2,42500+1000*self.length,(self.width*1000+4000+self.w1*1000)/2))
        self.cell.shapes(self.met1_layer).insert(pya.Box(40500+1000*self.length,(self.width*1000+14000-self.w1*1000)/2,42500+1000*self.length,(self.width*1000- 6000+self.w1*1000)/2))
        self.cell.shapes(self.via2_layer).insert(pya.Box(35500+1000*self.length,(self.width*1000+8000-self.w1*1000)/2,40500+1000*self.length,(self.width*1000+self.w1*1000)/2))
        self.cell.shapes(self.via3_layer).insert(pya.Box(33000+1000*self.length,(self.width*1000+3000-self.w1*1000)/2,43000+1000*self.length,(self.width*1000+5000+self.w1*1000)/2))
        
    if self.outMet2 == True:
        self.cell.shapes(self.met2_layer).insert(pya.Box(2000,(self.width*1000+6000-self.w1*1000)/2,9000,(self.width*1000+2000+self.w1*1000)/2))
        self.cell.shapes(self.via2_layer).insert(pya.Box(3000,(self.width*1000+8000-self.w1*1000)/2,8000,(self.width*1000+self.w1*1000)/2))
        self.cell.shapes(self.via3_layer).insert(pya.Box(500,(self.width*1000+3000-self.w1*1000)/2,10500,(self.width*1000+5000+self.w1*1000)/2))
        self.cell.shapes(self.met1_layer).insert(pya.Box(1000,(self.width*1000+4000-self.w1*1000)/2,10000,(self.width*1000+4000+self.w1*1000)/2))
        self.cell.shapes(self.met1_layer).insert(pya.Box(1000,(self.width*1000+14000-self.w1*1000)/2,3000,(self.width*1000-6000+self.w1*1000)/2))
        self.cell.shapes(self.via1_layer).insert(pya.Box(1500,(self.width*1000+5000-self.w1*1000)/2,9500,(self.width*1000+3000+self.w1*1000)/2))