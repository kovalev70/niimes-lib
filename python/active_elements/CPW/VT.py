import pya 

class VT(pya.PCellDeclarationHelper):
    
    def __init__(self):
        
        super(VT, self).__init__()
        
        self.via3 = pya.LayerInfo(72, 12, "Via3")
        self.ohmic = pya.LayerInfo(20, 1, "Ohmic")
        self.mesa = pya.LayerInfo(40, 2, "Mesa")
        self.dgate = pya.LayerInfo(51, 4, "Dgate")
        self.via1 = pya.LayerInfo(70, 6, "Via1")
        self.via2 = pya.LayerInfo(71, 11, "Via2")
        self.pad = pya.LayerInfo(50, 3, "Pad")
        self.met2 = pya.LayerInfo(92, 13, "Met2")
        self.met1 = pya.LayerInfo(91, 10, "Met1")
        
        self.param("via3", self.TypeLayer, "Layer of Via3", default=self.via3, hidden = True)
        self.param("ohmic", self.TypeLayer, "Layer of Ohmic", default=self.ohmic, hidden = True)
        self.param("mesa", self.TypeLayer, "Layer of Mesa", default=self.mesa, hidden = True)
        self.param("dgate", self.TypeLayer, "Layer of Dgate", default=self.dgate, hidden = True)
        self.param("via1", self.TypeLayer, "Layer of Via1", default=self.via1, hidden = True)
        self.param("via2", self.TypeLayer, "Layer of Via2", default=self.via2, hidden = True)
        self.param("pad", self.TypeLayer, "Layer of Pad", default=self.pad, hidden = True)
        self.param("met2", self.TypeLayer, "Layer of Met2", default=self.met2, hidden = True)
        self.param("met1", self.TypeLayer, "Layer of Met1", default=self.met1, hidden = True)

        self.param("length", self.TypeDouble, "Длина транзистора", default=50)
        self.param("NF", self.TypeDouble, "Кол-во пальцев", default=2, hidden = True)
        self.param("typeVT", self.TypeList, "Тип транзистора", default = 2, choices = [["VT2", 2], ["VT4", 4], ["VT6", 6], ["VT8", 8]])
        
    def display_text_impl(self):

        return (f'SUBCKT | ID=V1 | NET="VT{self.typeVT} | W={self.length} | NF={self.typeVT}')

    def coerce_parameters_impl(self):

        if (self.length < 15  or self.length > 125 ): 
            raise(RuntimeError("Ширина транзистора должна быть больше 15 и меньше 125"))

    def insertPolygons(self, pts_layer, layer):

        polygon = pya.SimplePolygon(pts_layer)
        self.cell.shapes(layer).insert(polygon)
        
    def produce_impl(self):
        
        if self.typeVT == 2:
            self.NF = 2
            self.cell.shapes(self.via3_layer).insert(pya.Box(0,11000,10500,32000))
            self.cell.shapes(self.via3_layer).insert(pya.Box(21000,0,20000+self.length*1000,12800))
            self.cell.shapes(self.via3_layer).insert(pya.Box(21000,30200,20000+self.length*1000,43000))
            self.cell.shapes(self.via3_layer).insert(pya.Box(31000+self.length*1000,17000,41000+self.length*1000,26000))
            self.cell.shapes(self.mesa_layer).insert(pya.Box(19500,2300,21500+self.length*1000,40700))

            for i in range(int(self.NF+1)):
                self.cell.shapes(self.ohmic_layer).insert(pya.Box(20500,3300+13200*i,20500+self.length*1000,13300+13200*i))
                self.cell.shapes(self.via1_layer).insert(pya.Box(22000,4800+i*13200,19000+self.length*1000,11800+i*13200))
                
            for i in range(int(self.NF)):
                self.cell.shapes(self.dgate_layer).insert(pya.Box(15500,14800+13200*i,25000+self.length*1000,15000+13200*i))
                self.cell.shapes(self.via1_layer).insert(pya.Box(10500,12900+i*13200,14500,16900+i*13200))
                pts_pad1 = [pya.Point(9500,11900+13200*i),pya.Point(15500,11900+13200*i),pya.Point(17500,13900+13200*i),
                            pya.Point(17500,15900+13200*i),pya.Point(15500,17900+13200*i),pya.Point(9500,17900+13200*i)]
                self.insertPolygons(pts_pad1, self.pad_layer)
                self.cell.shapes(self.met1_layer).insert(pya.Box(10000,12400+i*13200,15000,17400+i*13200))

            self.cell.shapes(self.via2_layer).insert(pya.Box(2500,13500,8000,29500))
            self.cell.shapes(self.via2_layer).insert(pya.Box(23500,2500,17500+self.length*1000,10300))
            self.cell.shapes(self.via2_layer).insert(pya.Box(23500,32700,17500+self.length*1000,40500))
            self.cell.shapes(self.via2_layer).insert(pya.Box(33500+self.length*1000,19500,38500+self.length*1000,23500))

        
            pts_pad11 = [pya.Point(24000+self.length*1000,13450),pya.Point(25500+self.length*1000,13450),pya.Point(25500+self.length*1000,15450),
                        pya.Point(23000+self.length*1000,15450),pya.Point(23000+self.length*1000,14450)]
                        
            pts_pad12 = [pya.Point(23000+self.length*1000,27550),pya.Point(25500+self.length*1000,27550),pya.Point(25500+self.length*1000,29550),
                         pya.Point(24000+self.length*1000,29550),pya.Point(23000+self.length*1000,28550)]
                                        
            self.insertPolygons(pts_pad11, self.pad_layer)
            self.insertPolygons(pts_pad12, self.pad_layer)
        
            self.cell.shapes(self.met2_layer).insert(pya.Box(1500,12500,9000,30500))
            self.cell.shapes(self.met2_layer).insert(pya.Box(32500+self.length*1000,18500,39500+self.length*1000,24500))
        
            if self.length < 36:
                self.cell.shapes(self.met2_layer).insert(pya.Box(22500,1500,18500+self.length*1000,11300))
                self.cell.shapes(self.met2_layer).insert(pya.Box(22500,31700,18500+self.length*1000,41500))
                self.cell.shapes(self.met2_layer).insert(pya.Box(23500,11300,32500,31700))
            
            if 36 <= self.length <= 60:
                self.cell.shapes(self.met2_layer).insert(pya.Box(22500,1500,18500+self.length*1000,11300))
                self.cell.shapes(self.met2_layer).insert(pya.Box(22500,31700,18500+self.length*1000,41500))
                self.cell.shapes(self.met2_layer).insert(pya.Box(28500,11300,40500,31700))
    
            if 61 <= self.length <= 125:
                self.cell.shapes(self.met2_layer).insert(pya.Box(22500,1500,18500+self.length*1000,11300))
                self.cell.shapes(self.met2_layer).insert(pya.Box(22500,31700,18500+self.length*1000,41500))
                self.cell.shapes(self.met2_layer).insert(pya.Box(28500,11300,42500,31700))
           
            if 61 <= self.length <= 80:
                self.cell.shapes(self.met2_layer).insert(pya.Box(58500,11300,72500,31700))
  
            if 81 <= self.length <= 90:
                self.cell.shapes(self.met2_layer).insert(pya.Box(68500,11300,82500,31700))
     
            if 91 <= self.length <= 100:
                self.cell.shapes(self.met2_layer).insert(pya.Box(76500,11300,90500,31700))
   
            if 101 <= self.length <= 110:
                self.cell.shapes(self.met2_layer).insert(pya.Box(61500,11300,75500,31700))
                self.cell.shapes(self.met2_layer).insert(pya.Box(99500,11300,113500,31700))
            
            if 111 <= self.length <= 120:
               self.cell.shapes(self.met2_layer).insert(pya.Box(66500,11300,80500,31700))
               self.cell.shapes(self.met2_layer).insert(pya.Box(104500,11300,118500,31700))
            
            if 121 <= self.length <= 125:
               self.cell.shapes(self.met2_layer).insert(pya.Box(71500,11300,85500,31700))
               self.cell.shapes(self.met2_layer).insert(pya.Box(119500,11300,133500,31700))
        
            self.cell.shapes(self.met1_layer).insert(pya.Box(500,11500,10000,31500))
            self.cell.shapes(self.met1_layer).insert(pya.Box(21500,500,19500+self.length*1000,12300))
            self.cell.shapes(self.met1_layer).insert(pya.Box(21500,30700,19500+self.length*1000,42500))
            self.cell.shapes(self.met1_layer).insert(pya.Box(21500,17500,40500+self.length*1000,25500))

        if self.typeVT == 4:
            self.NF = 4

            self.cell.shapes(self.via3_layer).insert(pya.Box(0,11000,10500,59000))
            self.cell.shapes(self.via3_layer).insert(pya.Box(21000,0,20000+self.length*1000,13100))
            self.cell.shapes(self.via3_layer).insert(pya.Box(21000,30500,20000+self.length*1000,39500))
            self.cell.shapes(self.via3_layer).insert(pya.Box(21000,56900,20000+self.length*1000,70000))
            self.cell.shapes(self.via3_layer).insert(pya.Box(31000+self.length*1000,16000,41000+self.length*1000,54000))

            for i in range(self.NF+1):
                self.cell.shapes(self.ohmic_layer).insert(pya.Box(20500,3600+13200*i,20500+self.length*1000,13600+13200*i))
                self.cell.shapes(self.via1_layer).insert(pya.Box(22000,5100+i*13200,19000+self.length*1000,12100+i*13200))

            self.cell.shapes(self.mesa_layer).insert(pya.Box(19500,2600,21500+self.length*1000,67400))

            for i in range(int(self.NF)):
               self.cell.shapes(self.via1_layer).insert(pya.Box(10500,13200+i*13200,14500,17200+i*13200))
               self.cell.shapes(self.dgate_layer).insert(pya.Box(15500,15100+13200*i,25000+self.length*1000,15300+13200*i))
               pts_pad1 = [pya.Point(9500,12200+13200*i),pya.Point(15500,12200+13200*i),pya.Point(17500,14200+13200*i),
                          pya.Point(17500,16200+13200*i),pya.Point(15500,18200+13200*i),pya.Point(9500,18200+13200*i)]
               self.insertPolygons(pts_pad1, self.pad_layer)
               self.cell.shapes(self.met1_layer).insert(pya.Box(10000,12700+i*13200,15000,17700+i*13200))
              
            self.cell.shapes(self.via2_layer).insert(pya.Box(2500,13500,8000,56500))
            self.cell.shapes(self.via2_layer).insert(pya.Box(23500,2500,17500+self.length*1000,10600))
            self.cell.shapes(self.via2_layer).insert(pya.Box(23500,33000,17500+self.length*1000,37000))
            self.cell.shapes(self.via2_layer).insert(pya.Box(23500,59400,17500+self.length*1000,67500))
            self.cell.shapes(self.via2_layer).insert(pya.Box(33500+self.length*1000,18500,38500+self.length*1000,51500))
                
            for i in range(int(self.NF//2)):
                pts_pad11 = [pya.Point(24000+self.length*1000,13750+i*26400),pya.Point(25500+self.length*1000,13850+i*26300),pya.Point(25500+self.length*1000,15750+i*26400),
                             pya.Point(23000+self.length*1000,15750+i*26400),pya.Point(23000+self.length*1000,14750+i*26400)]
                         
                pts_pad12 = [pya.Point(23000+self.length*1000,27850+i*26400),pya.Point(25500+self.length*1000,27850+i*26400),pya.Point(25500+self.length*1000,29850+i*26400),
                             pya.Point(24000+self.length*1000,29850+i*26400),pya.Point(23000+self.length*1000,28850+i*26400)]
                self.insertPolygons(pts_pad11, self.pad_layer)
                self.insertPolygons(pts_pad12, self.pad_layer)
                self.cell.shapes(self.met1_layer).insert(pya.Box(21500,17800+i*26400,31500+self.length*1000,25800+i*26400))

            self.cell.shapes(self.met2_layer).insert(pya.Box(1500,12500,9000,57500))
            self.cell.shapes(self.met2_layer).insert(pya.Box(32500+self.length*1000,17500,39500+self.length*1000,52500))
        
            pts_met21 = [pya.Point(22500,1500),pya.Point(22500,11600),pya.Point(23500,11600),
                        pya.Point(23500,32000),pya.Point(22500,32000),pya.Point(22500,38000),
                        pya.Point(23500,38000),pya.Point(23500,58400),pya.Point(22500,58400),
                        pya.Point(22500,68500),pya.Point(18500+self.length*1000,68500),pya.Point(18500+self.length*1000,58400),
                        pya.Point(32500,58400),pya.Point(32500,38000),pya.Point(18500+self.length*1000,38000),
                        pya.Point(18500+self.length*1000,32000),pya.Point(32500,32000),pya.Point(32500,11600),
                        pya.Point(18500+self.length*1000,11600),pya.Point(18500+self.length*1000,1500),]
                     
            if self.length < 36:
                self.insertPolygons(pts_met21, self.met2_layer)

            pts_met22 = [pya.Point(22500,1500),pya.Point(22500,11600),pya.Point(28500,11600),
                         pya.Point(28500,32000),pya.Point(22500,32000),pya.Point(22500,38000),
                         pya.Point(28500,38000),pya.Point(28500,58400),pya.Point(22500,58400),
                         pya.Point(22500,68500),pya.Point(18500+self.length*1000,68500),pya.Point(18500+self.length*1000,58400),
                         pya.Point(40500,58400),pya.Point(40500,38000),pya.Point(18500+self.length*1000,38000),
                         pya.Point(18500+self.length*1000,32000),pya.Point(40500,32000),pya.Point(40500,11600),
                         pya.Point(18500+self.length*1000,11600),pya.Point(18500+self.length*1000,1500),]
            if 36 <= self.length <= 60:
                self.insertPolygons(pts_met22, self.met2_layer)
        
            if 61 <= self.length <= 125:
                self.cell.shapes(self.met2_layer).insert(pya.Box(22500,1500,18500+self.length*1000,11600))
                self.cell.shapes(self.met2_layer).insert(pya.Box(22500,32000,18500+self.length*1000,38000))
                self.cell.shapes(self.met2_layer).insert(pya.Box(22500,58400,18500+self.length*1000,68500))
                self.cell.shapes(self.met2_layer).insert(pya.Box(28500,11600,42500,32000))
                self.cell.shapes(self.met2_layer).insert(pya.Box(28500,38000,42500,58400))
        
            if 61 <= self.length <= 80:
                self.cell.shapes(self.met2_layer).insert(pya.Box(58500,11600,72500,32000))
                self.cell.shapes(self.met2_layer).insert(pya.Box(58500,38000,72500,58400))
            
            if 81 <= self.length <= 90:
                self.cell.shapes(self.met2_layer).insert(pya.Box(68500,11600,82500,32000))
                self.cell.shapes(self.met2_layer).insert(pya.Box(68500,38000,82500,58400))
            
            if 91 <= self.length <= 100:
                self.cell.shapes(self.met2_layer).insert(pya.Box(76500,11600,90500,32000))
                self.cell.shapes(self.met2_layer).insert(pya.Box(76500,38000,90500,58400))
            
            if 101 <= self.length <= 110:
                self.cell.shapes(self.met2_layer).insert(pya.Box(61500,11600,75500,32000))
                self.cell.shapes(self.met2_layer).insert(pya.Box(61500,38000,75500,58400))
                self.cell.shapes(self.met2_layer).insert(pya.Box(99500,11600,113500,32000))
                self.cell.shapes(self.met2_layer).insert(pya.Box(99500,38000,113500,58400))
                
            if 111 <= self.length <= 120:
                self.cell.shapes(self.met2_layer).insert(pya.Box(66500,11600,80500,32000))
                self.cell.shapes(self.met2_layer).insert(pya.Box(66500,38000,80500,58400))
                self.cell.shapes(self.met2_layer).insert(pya.Box(104500,11600,118500,32000))
                self.cell.shapes(self.met2_layer).insert(pya.Box(104500,38000,118500,58400))
            
            if 121 <= self.length <= 125:
                self.cell.shapes(self.met2_layer).insert(pya.Box(71500,11600,85500,32000))
                self.cell.shapes(self.met2_layer).insert(pya.Box(71500,38000,85500,58400))
                self.cell.shapes(self.met2_layer).insert(pya.Box(119500,11600,133500,32000))
                self.cell.shapes(self.met2_layer).insert(pya.Box(119500,38000,133500,58400))
        
            self.cell.shapes(self.met1_layer).insert(pya.Box(500,11500,10000,58500))
            self.cell.shapes(self.met1_layer).insert(pya.Box(21500,500,19500+self.length*1000,12600))
            self.cell.shapes(self.met1_layer).insert(pya.Box(21500,57400,19500+self.length*1000,69500))
            self.cell.shapes(self.met1_layer).insert(pya.Box(21500,31000,19500+self.length*1000,39000))
             
            self.cell.shapes(self.met1_layer).insert(pya.Box(31500+self.length*1000,16500,40500+self.length*1000,53500))
    
        if self.typeVT == 6:
            self.NF = 6
            self.cell.shapes(self.via3_layer).insert(pya.Box(0,12000,10500,86000))
            self.cell.shapes(self.via3_layer).insert(pya.Box(21000,0,20000+self.length*1000,13900))
            self.cell.shapes(self.via3_layer).insert(pya.Box(21000,84100,20000+self.length*1000,98000))
            self.cell.shapes(self.via3_layer).insert(pya.Box(31000+self.length*1000,17000,41000+self.length*1000,81000))
            
            for i in range(int((self.NF//2)-1)):
                self.cell.shapes(self.via3_layer).insert(pya.Box(21000,31300+26400*i,20000+self.length*1000,40300+26400*i))

            for i in range(self.NF+1):
                self.cell.shapes(self.ohmic_layer).insert(pya.Box(20500,4400+13200*i,20500+self.length*1000,14400+13200*i))
                self.cell.shapes(self.via1_layer).insert(pya.Box(22000,5900+i*13200,19000+self.length*1000,12900+i*13200))
            
            self.cell.shapes(self.mesa_layer).insert(pya.Box(19500,3400,21500+self.length*1000,94600))
        
            for i in range(self.NF):
                self.cell.shapes(self.dgate_layer).insert(pya.Box(15500,15900+13200*i,25000+self.length*1000,16100+13200*i))
                self.cell.shapes(self.via1_layer).insert(pya.Box(10500,14000+i*13200,14500,18000+i*13200))
                pts_pad1 = [pya.Point(9500,13000+13200*i),pya.Point(15500,13000+13200*i),pya.Point(17500,15000+13200*i),
                            pya.Point(17500,17000+13200*i),pya.Point(15500,19000+13200*i),pya.Point(9500,19000+13200*i)]
                self.insertPolygons(pts_pad1, self.pad_layer)
                self.cell.shapes(self.met1_layer).insert(pya.Box(10000,13500+i*13200,15000,18500+i*13200))
            
            self.cell.shapes(self.via2_layer).insert(pya.Box(2500,14500,8000,83500))
            self.cell.shapes(self.via2_layer).insert(pya.Box(23500,2500,17500+self.length*1000,11400))
        
            for i in range(int(self.NF//3)):
                self.cell.shapes(self.via2_layer).insert(pya.Box(23500,33800+i*26400,17500+self.length*1000,37800+i*26400))
            
            self.cell.shapes(self.via2_layer).insert(pya.Box(23500,86600,17500+self.length*1000,95500))
            self.cell.shapes(self.via2_layer).insert(pya.Box(33500+self.length*1000,19500,38500+self.length*1000,78500))
                  
            for i in range(int(self.NF//2)):
                pts_pad11 = [pya.Point(24000+self.length*1000,14550+i*26400),pya.Point(25500+self.length*1000,14550+i*26400),pya.Point(25500+self.length*1000,16550+i*26400),
                             pya.Point(23000+self.length*1000,16550+i*26400),pya.Point(23000+self.length*1000,15550+i*26400)]
                     
                pts_pad12 = [pya.Point(23000+self.length*1000,28650+i*26400),pya.Point(25500+self.length*1000,28650+i*26400),pya.Point(25500+self.length*1000,30650+i*26400),
                             pya.Point(24000+self.length*1000,30650+i*26400),pya.Point(23000+self.length*1000,29650+i*26400)]
                self.insertPolygons(pts_pad11, self.pad_layer)
                self.insertPolygons(pts_pad12, self.pad_layer)
                self.cell.shapes(self.met1_layer).insert(pya.Box(21500,18600+i*26400,31500+self.length*1000,26600+i*26400))
                     
            self.cell.shapes(self.met2_layer).insert(pya.Box(1500,13500,9000,84500))
            self.cell.shapes(self.met2_layer).insert(pya.Box(32500+self.length*1000,18500,39500+self.length*1000,79500))
            self.cell.shapes(self.met2_layer).insert(pya.Box(22500,1500,18500+self.length*1000,12400))
            self.cell.shapes(self.met2_layer).insert(pya.Box(22500,85600,18500+self.length*1000,96500))
        
            for i in range(2):
                self.cell.shapes(self.met2_layer).insert(pya.Box(22500,32800+i*26400,18500+self.length*1000,38800+i*26400))
                
            if self.length < 36:
                for i in range(3):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(23500,12400+i*26400,32500,32800+i*26400))
            
            if 36 <= self.length <= 60:
                for i in range(3):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(28500,12400+i*26400,40500,32800+i*26400))

            if 61 <= self.length <= 125:
                for i in range(3):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(28500,12400+i*26400,42500,32800+i*26400))

            if 61 <= self.length <= 80:
                for i in range(3):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(58500,12400+i*26400,72500,32800+i*26400))
  
            if 81 <= self.length <= 90:
                for i in range(3):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(68500,12400+i*26400,82500,32800+i*26400))
     
            if 91 <= self.length <= 100:
                for i in range(3):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(76500,12400+i*26400,90500,32800+i*26400))
   
            if 101 <= self.length <= 110:
                for i in range(3):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(61500,12400+i*26400,75500,32800+i*26400))
                for i in range(3):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(99500,12400+i*26400,113500,32800+i*26400))
            
            if 111 <= self.length <= 120:
                for i in range(3):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(66500,12400+i*26400,80500,32800+i*26400))
                for i in range(3):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(109500,12400+i*26400,123500,32800+i*26400))
            
            if 121 <= self.length <= 125:
                for i in range(3):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(71500,12400+i*26400,85500,32800+i*26400))
                for i in range(3):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(119500,12400+i*26400,133500,32800+i*26400))
        
            self.cell.shapes(self.met1_layer).insert(pya.Box(500,12500,10000,85500))
            self.cell.shapes(self.met1_layer).insert(pya.Box(21500,500,19500+self.length*1000,13400))
            self.cell.shapes(self.met1_layer).insert(pya.Box(21500,84600,19500+self.length*1000,97500))
         
            self.cell.shapes(self.met1_layer).insert(pya.Box(31500+self.length*1000,17500,40500+self.length*1000,80500))

            for i in range(int(2)):
                self.cell.shapes(self.met1_layer).insert(pya.Box(21500,31800+i*26400,self.length*1000+19500,39800+i*26400))
                
       
        if self.typeVT == 8:
            self.NF = 8
            self.cell.shapes(self.via3_layer).insert(pya.Box(0,12000,10500,111000))
            self.cell.shapes(self.via3_layer).insert(pya.Box(21000,0,20000+self.length*1000,13200))
            self.cell.shapes(self.via3_layer).insert(pya.Box(21000,109800,20000+self.length*1000,123000))
            self.cell.shapes(self.via3_layer).insert(pya.Box(31000+self.length*1000,17000,41000+self.length*1000,106000))
            
            for i in range(int((self.NF//2)-1)):
              self.cell.shapes(self.via3_layer).insert(pya.Box(21000,30600+26400*i,20000+self.length*1000,39600+26400*i))
    
            for i in range(self.NF+1):
                self.cell.shapes(self.ohmic_layer).insert(pya.Box(20500,3700+13200*i,20500+self.length*1000,13700+13200*i))
                self.cell.shapes(self.via1_layer).insert(pya.Box(22000,5200+i*13200,19000+self.length*1000,12200+i*13200))
                
            self.cell.shapes(self.mesa_layer).insert(pya.Box(19500,2700,21500+self.length*1000,120300))
            
            for i in range(self.NF):
                self.cell.shapes(self.dgate_layer).insert(pya.Box(15500,15200+13200*i,25000+self.length*1000,15400+13200*i))
                self.cell.shapes(self.via1_layer).insert(pya.Box(10500,13300+i*13200,14500,17300+i*13200))
                pts_pad1 = [pya.Point(9500,12300+13200*i),pya.Point(15500,12300+13200*i),pya.Point(17500,14300+13200*i),
                            pya.Point(17500,16300+13200*i),pya.Point(15500,18300+13200*i),pya.Point(9500,18300+13200*i)]
                self.insertPolygons(pts_pad1, self.pad_layer)
                self.cell.shapes(self.met1_layer).insert(pya.Box(10000,12800+i*13200,15000,17800+i*13200))
                
            self.cell.shapes(self.via2_layer).insert(pya.Box(2500,14500,8000,108500))
            self.cell.shapes(self.via2_layer).insert(pya.Box(23500,2500,17500+self.length*1000,10700))
            
            for i in range(int(3)):
                self.cell.shapes(self.via2_layer).insert(pya.Box(23500,33100+i*26400,17500+self.length*1000,37100+i*26400))
                
            self.cell.shapes(self.via2_layer).insert(pya.Box(23500,112300,17500+self.length*1000,120500))
            self.cell.shapes(self.via2_layer).insert(pya.Box(33500+self.length*1000,19500,38500+self.length*1000,103500))
            

            for i in range(int(self.NF//2)):
                pts_pad11 = [pya.Point(24000+self.length*1000,13850+i*26400),pya.Point(25500+self.length*1000,13850+i*26400),pya.Point(25500+self.length*1000,15850+i*26400),
                             pya.Point(23000+self.length*1000,15850+i*26400),pya.Point(23000+self.length*1000,14850+i*26400)]
                         
                pts_pad12 = [pya.Point(23000+self.length*1000,27950+i*26400),pya.Point(25500+self.length*1000,27950+i*26400),pya.Point(25500+self.length*1000,29950+i*26400),
                             pya.Point(24000+self.length*1000,29950+i*26400),pya.Point(23000+self.length*1000,28950+i*26400)]
                self.insertPolygons(pts_pad11, self.pad_layer)
                self.insertPolygons(pts_pad12, self.pad_layer)
                self.cell.shapes(self.met1_layer).insert(pya.Box(21500,17900+i*26400,31500+self.length*1000,25900+i*26400))
                         
            self.cell.shapes(self.met2_layer).insert(pya.Box(1500,13500,9000,109500))
            self.cell.shapes(self.met2_layer).insert(pya.Box(32500+self.length*1000,18500,39500+self.length*1000,104500))
            self.cell.shapes(self.met2_layer).insert(pya.Box(22500,1500,18500+self.length*1000,11700))
            self.cell.shapes(self.met2_layer).insert(pya.Box(22500,111300,18500+self.length*1000,121500))
            
            for i in range(3):
                self.cell.shapes(self.met2_layer).insert(pya.Box(22500,32100+i*26400,18500+self.length*1000,38100+i*26400))
            if self.length < 36:
                for i in range(4):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(23500,11700+i*26400,32500,32100+i*26400))
                
            if 36 <= self.length <= 60:
                for i in range(4):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(28500,11700+i*26400,40500,32100+i*26400))
    
            if 61 <= self.length <= 125:
                for i in range(4):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(28500,11700+i*26400,42500,32100+i*26400))
    
            if 61 <= self.length <= 80:
                for i in range(4):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(58500,11700+i*26400,72500,32100+i*26400))
      
            if 81 <= self.length <= 90:
                for i in range(4):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(68500,11700+i*26400,82500,32100+i*26400))
         
            if 91 <= self.length <= 100:
                for i in range(4):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(76500,11700+i*26400,90500,32100+i*26400))
       
            if 101 <= self.length <= 110:
                for i in range(4):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(61500,11700+i*26400,75500,32100+i*26400))
                for i in range(4):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(99500,11700+i*26400,113500,32100+i*26400))
                
            if 111 <= self.length <= 120:
                for i in range(4):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(66500,11700+i*26400,80500,32100+i*26400))
                for i in range(4):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(109500,11700+i*26400,123500,32100+i*26400))
                
            if 121 <= self.length <= 125:
                for i in range(4):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(71500,11700+i*26400,85500,32100+i*26400))
                for i in range(4):
                    self.cell.shapes(self.met2_layer).insert(pya.Box(119500,11700+i*26400,133500,32100+i*26400))
            
            self.cell.shapes(self.met1_layer).insert(pya.Box(500,12500,10000,110500))
            self.cell.shapes(self.met1_layer).insert(pya.Box(21500,500,19500+self.length*1000,12700))
            self.cell.shapes(self.met1_layer).insert(pya.Box(21500,110300,19500+self.length*1000,122500))
             
            self.cell.shapes(self.met1_layer).insert(pya.Box(31500+self.length*1000,17500,40500+self.length*1000,105500))

            for i in range(int(3)):
                self.cell.shapes(self.met1_layer).insert(pya.Box(21500,31100+i*26400,self.length*1000+19500,39100+i*26400))