import pya 

class BACKVIA(pya.PCellDeclarationHelper):
    
    def __init__(self):
        
        super(BACKVIA, self).__init__()
        
        self.backVia = pya.LayerInfo(120, 15, "BackVia")
        self.via2 = pya.LayerInfo(71, 11, "Via2")
        self.met2 = pya.LayerInfo(92, 13, "Met2")
        self.via1 = pya.LayerInfo(70, 6, "Via1")
        self.met1 = pya.LayerInfo(91, 10, "Met1")
        self.via3 = pya.LayerInfo(72, 12, "Via3")
        self.ohmic = pya.LayerInfo(20, 1, "Ohmic")
        self.mesa = pya.LayerInfo(40, 2, "Mesa")

        self.param("backVia", self.TypeLayer, "Layer of BackVia", default=self.backVia, hidden=True)
        self.param("via2", self.TypeLayer, "Layer of Via2", default=self.via2, hidden=True)
        self.param("met2", self.TypeLayer, "Layer of Met2", default=self.met2, hidden=True)
        self.param("via1", self.TypeLayer, "Layer of Via1", default=self.via1, hidden=True)
        self.param("met1", self.TypeLayer, "Layer of Met1", default=self.met1, hidden=True)
        self.param("via3", self.TypeLayer, "Layer of Via3", default=self.via3, hidden=True)
        self.param("ohmic", self.TypeLayer, "Layer of Ohmic", default=self.ohmic, hidden=True)
        self.param("mesa", self.TypeLayer, "Layer of Mesa", default=self.mesa, hidden=True)

        self.param("nPorts", self.TypeBoolean, "4 выхода", default=False)
        
    def display_text_impl(self):

        return (f'SUBCKT')
      
    def produce_impl(self):

        self.cell.shapes(self.via2_layer).insert(pya.Box(pya.Point(-47000, -32000), pya.Point(47000, 32000)))
        self.cell.shapes(self.met2_layer).insert(pya.Box(pya.Point(-48000, -33000), pya.Point(48000, 33000)))
        self.cell.shapes(self.via1_layer).insert(pya.Box(pya.Point(-48500, -33500), pya.Point(48500, 33500)))
        self.cell.shapes(self.met1_layer).insert(pya.Box(pya.Point(-49000, -34000), pya.Point(49000, 34000)))
        self.cell.shapes(self.via3_layer).insert(pya.Box(pya.Point(-49500, -34500), pya.Point(49500, 34500)))
        self.cell.shapes(self.ohmic_layer).insert(pya.Box(pya.Point(-50000, -35000), pya.Point(50000, 35000)))
        self.cell.shapes(self.mesa_layer).insert(pya.Box(pya.Point(-51000, -36000), pya.Point(51000, 36000)))
        
        pts_backVia = [pya.Point(-30000, -15000), pya.Point(-30000, 15000), pya.Point(30000, 15000), pya.Point(30000, -15000)]
        backVia_Polygon = pya.Polygon(pts_backVia)

        self.cell.shapes(self.backVia_layer).insert(backVia_Polygon.round_corners(0, 15000, 32))

        if self.nPorts == True:
            self.cell.shapes(self.met1_layer).insert(pya.Box(pya.Point(-49000, -1000), pya.Point(-47000, 1000)))
            self.cell.shapes(self.met1_layer).insert(pya.Box(pya.Point(-1000, 32000), pya.Point(1000, 34000)))
            self.cell.shapes(self.met1_layer).insert(pya.Box(pya.Point(47000, -1000), pya.Point(49000, 1000)))
            self.cell.shapes(self.met1_layer).insert(pya.Box(pya.Point(1000, -32000), pya.Point(-1000, -34000)))