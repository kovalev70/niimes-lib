import pya

class PAD(pya.PCellDeclarationHelper):

  def __init__(self):

    super(PAD, self).__init__()
    
    self.met1 = pya.LayerInfo(91, 10, "Met1")
    self.met2 = pya.LayerInfo(92, 13, "Met2")
    self.via2 = pya.LayerInfo(71, 11, "Via2")
    self.via3 = pya.LayerInfo(72, 12, "Via3")
    self.via4 = pya.LayerInfo(73, 14, "Via4")
    
    self.param("met1", self.TypeLayer, "Layer of met1", default=self.met1, hidden=True)
    self.param("met2", self.TypeLayer, "Layer of met1", default=self.met2, hidden=True)
    self.param("via2", self.TypeLayer, "Layer of via2", default=self.via2, hidden=True)
    self.param("via3", self.TypeLayer, "Layer of via3", default=self.via3, hidden=True)
    self.param("via4", self.TypeLayer, "Layer of via4", default=self.via4, hidden=True)
    
    self.param("width", self.TypeInt, "Ширина контактной площадки", default=100)
    self.param("length", self.TypeInt, "Длина контактной площадки", default=100)
    
  def coerce_parameters_impl(self):
    
    if (self.width < 75 or self.width > 250):
      raise(RuntimeError("Высота должна быть задана в диапазоне от 75 до 250"))
      
    if (self.length < 75 or self.length > 250):
      raise(RuntimeError("Ширина должна быть задана в диапазоне от 75 до 250"))
      
  def display_text_impl(self):
  
    return (f'SUBCKT | ID=X1 | NET="PAD" | W={self.width} | L={self.length}')
    
  def produce_impl(self):
  
    pts_via4 = [pya.Point(self.length * -500, self.width * -500), pya.Point(self.length * 500, self.width * 500)]
    pts_via2 = [pya.Point(pts_via4[0].x - 4000, pts_via4[0].y - 4000), pya.Point(pts_via4[1].x + 4000, pts_via4[1].y + 4000)]
    pts_met2 = [pya.Point(pts_via4[0].x - 5000, pts_via4[0].y - 5000), pya.Point(pts_via4[1].x + 5000, pts_via4[1].y + 5000)]
    pts_met1 = [pya.Point(pts_via4[0].x - 6000, pts_via4[0].y - 6000), pya.Point(pts_via4[1].x + 6000, pts_via4[1].y + 6000)]
    pts_via3 = [pya.Point(pts_via4[0].x - 6500, pts_via4[0].y - 6500), pya.Point(pts_via4[1].x + 6500, pts_via4[1].y + 6500)]
    
    self.cell.shapes(self.via4_layer).insert(pya.Box(pts_via4[0], pts_via4[1]))
    self.cell.shapes(self.via2_layer).insert(pya.Box(pts_via2[0], pts_via2[1]))
    self.cell.shapes(self.met2_layer).insert(pya.Box(pts_met2[0], pts_met2[1]))
    self.cell.shapes(self.met1_layer).insert(pya.Box(pts_met1[0], pts_met1[1]))
    self.cell.shapes(self.via3_layer).insert(pya.Box(pts_via3[0], pts_via3[1]))