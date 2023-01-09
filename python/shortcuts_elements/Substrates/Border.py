import pya 

class Border(pya.PCellDeclarationHelper):
    
    def __init__(self):
        
        super(Border, self).__init__()
        
        self.backVia = pya.LayerInfo(120, 15, "BackVia")
        self.via2 = pya.LayerInfo(71, 11, "Via2")
        self.via1 = pya.LayerInfo(70, 6, "Via1")
        self.via3 = pya.LayerInfo(72, 12, "Via3")
        self.via4 = pya.LayerInfo(73, 14, "Via4")
        self.border = pya.LayerInfo(140, 17, "Border")
        self.back = pya.LayerInfo(130, 16, "Back")

        self.param("via2", self.TypeLayer, "Layer of Via2", default=self.via2, hidden=True)
        self.param("via1", self.TypeLayer, "Layer of Via1", default=self.via1, hidden=True)
        self.param("via3", self.TypeLayer, "Layer of Via3", default=self.via3, hidden=True)
        self.param("via4", self.TypeLayer, "Layer of Via4", default=self.via4, hidden=True)
        self.param("border", self.TypeLayer, "Layer of Border", default=self.border, hidden=True)
        self.param("back", self.TypeLayer, "Layer of Back", default=self.back, hidden=True)
        
        self.param("l", self.TypeDouble, "Длина Border", default=1000)
        self.param("w", self.TypeDouble, "Ширина Border", default=1000)
        
    def display_text_impl(self):

        return (f'SUBCKT | ID=B1 | L={self.l} | W={self.w}')
      
    def produce_impl(self):
    
        pts_via1 = [pya.Point(30500,0),pya.Point(30500,self.w*1000-30500+100000),pya.Point(self.l*1000-30500+100000,self.w*1000-30500+100000),
                    pya.Point(self.l*1000-30500+100000,30500),pya.Point(61000,30500)]
        pts_via2 = [pya.Point(29000,0),pya.Point(29000,self.w*1000-29000+100000),pya.Point(self.l*1000-29000+100000,self.w*1000-29000+100000),
                    pya.Point(self.l*1000-29000+100000,29000),pya.Point(58000,29000)]
        pts_via3 = [pya.Point(33000,0),pya.Point(33000,self.w*1000-33000+100000),pya.Point(self.l*1000-33000+100000,self.w*1000-33000+100000),
                    pya.Point(self.l*1000-33000+100000,33000),pya.Point(66000,33000)]
        pts_via4 = [pya.Point(27500,0),pya.Point(27500,self.w*1000-27500+100000),pya.Point(self.l*1000-27500+100000,self.w*1000-27500+100000),
                    pya.Point(self.l*1000-27500+100000,27500),pya.Point(55000,27500)]
        pts_back = [pya.Point(25000,0),pya.Point(25000,self.w*1000-25000+100000),pya.Point(self.l*1000-25000+100000,self.w*1000-25000+100000),
                    pya.Point(self.l*1000-25000+100000,25000),pya.Point(50000,25000)]
        
        self.cell.shapes(self.border_layer).insert(pya.Box(0,0,self.l*1000+100000 ,self.w*1000+100000))
        self.cell.shapes(self.via1_layer).insert(pya.Path(pts_via1, 61000)) 
        self.cell.shapes(self.via2_layer).insert(pya.Path(pts_via2, 58000))
        self.cell.shapes(self.via3_layer).insert(pya.Path(pts_via3, 66000))
        self.cell.shapes(self.via4_layer).insert(pya.Path(pts_via4, 55000))
        self.cell.shapes(self.back_layer).insert(pya.Path(pts_back, 50000))