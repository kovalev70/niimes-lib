import pya

class Rost_EM_Rectangular(pya.PCellDeclarationHelper):

  def __init__(self):

    super(Rost_EM_Rectangular, self).__init__()
    
    self.met1 = pya.LayerInfo(91, 10, "Met1")
    self.met2 = pya.LayerInfo(92, 13, "Met2")
    self.via2 = pya.LayerInfo(71, 11, "Via2")
    self.via3 = pya.LayerInfo(72, 12, "Via3")
    
    self.param("met1", self.TypeLayer, "Layer of met1", default=self.met1, hidden=True)
    self.param("met2", self.TypeLayer, "Layer of met2", default=self.met2, hidden=True)
    self.param("via2", self.TypeLayer, "Layer of via2", default=self.via2, hidden=True)
    self.param("via3", self.TypeLayer, "Layer of via3", default=self.via3, hidden=True)
    
    self.param("Rd", self.TypeInt, "Внутреннее расстояние между противоположными сторонами", default=40)
    self.param("W", self.TypeInt, "Ширина линии", default=7)
    self.param("S", self.TypeInt, "Зазор между витками", default=7)
    self.param("Nt", self.TypeDouble, "Количество витков", default=2.5)
    self.param("Lout", self.TypeInt, "Длина первого сегмента вывода 1", default=16)
    self.param("Ln", self.TypeInt, "Длина выходного сегмента вывода 2", default=16)
    self.param("L1m", self.TypeInt, "Сдвиг вывода, относительно Rd", default=4) 
    self.param("Lbx", self.TypeInt, "Свдиг 2 вывода", default=0) 
    self.param("Lin", self.TypeInt, "Сдвиг 1 вывода", default=0)

  def insertBoxes(self, pts_layer, layer):
    
    i = len(pts_layer)
    while i >= 0:
      self.cell.shapes(layer).insert(pya.Box(pts_layer[i - 2], pts_layer[i - 1]))
      i -= 2

  def display_text_impl(self):
  
    return (f'SUBCKT | ID=L1 | NET="L_sq_scal" | Rd={self.Rd} | W={self.W} | S={self.S} | Nt={self.Nt} | Lout={self.Lout} | Ln={self.Ln} | L1m={self.L1m} | Lbx={self.Lbx} | Lin={self.Lin}')
    
  def coerce_parameters_impl(self):

        if (self.Rd < 25 or self.Rd > 150): 
            raise(RuntimeError("Внутреннее растояние должно принимиать значения в диапазоне от 25 до 150"))

        if (self.Nt < 1.5 or self.Nt > 19.5): 
            raise(RuntimeError("Количество витков должно принимиать значения в диапазоне от 1.5 до 19.5"))

        if (self.Nt % 0.25 != 0): 
            raise(RuntimeError("Количество витков должно быть кратно 0.25"))
            
        if (self.W < 7 or self.W > 40):
            raise(RuntimeError("Ширина должна быть задана в диапазоне от 7 до 40"))
            
        if (self.S < 7 or self.S > 40):
            raise(RuntimeError("Зазор должен быть задан в диапазоне от 7 до 40"))
    
  def produce_impl(self):
    
    num_points = self.Nt / 0.25
    cur_point = 2
    cur_direction = 1
    
    kW = num_points / 2
    kS = num_points / 2 - 1

    kW2 = kW // 2
    kS2 = kS // 2

    pts_met2 = [pya.Point(0,0)]
    pts_met2.append(pya.Point(0, (-self.Lout - 0.5) * 1000))

    while cur_point != num_points + 1:

      if cur_direction == 1:
        pts_met2.append(pya.Point(pts_met2[cur_point - 1].x + (self.Rd - self.L1m + kW * self.W + kS * self.S) * 1000, pts_met2[cur_point - 1].y))
        cur_point += 1
        cur_direction += 1
        kW -= 1
        kS -= 1
        
      elif cur_direction == 2:
        pts_met2.append(pya.Point(pts_met2[cur_point - 1].x, pts_met2[cur_point - 1].y + (self.Rd + kW * self.W + kS * self.S) * 1000)) 
        cur_point += 1
        cur_direction += 1

      elif cur_direction == 3:
        pts_met2.append(pya.Point(pts_met2[cur_point - 1].x - (self.Rd - self.L1m + kW * self.W + kS * self.S) * 1000, pts_met2[cur_point - 1].y))
        cur_point += 1
        cur_direction += 1
        kW -= 1
        kS -= 1

      elif cur_direction == 4:
        pts_met2.append(pya.Point(pts_met2[cur_point - 1].x, pts_met2[cur_point - 1].y - (self.Rd + kW * self.W + kS * self.S) * 1000))
        cur_point += 1
        cur_direction = 1

    pts_met1 = [pya.Point(pts_met2[0].x - (self.W / 2 + 1) * 1000, pts_met2[0].y - (self.W + 1) * 1000), pya.Point(pts_met2[0].x + (self.W / 2 + 1) * 1000, pts_met2[0].y + 1000)]
    pts_via2 = [pya.Point(pts_met1[0].x + 2000, pts_met1[0].y + 2000), pya.Point(pts_met1[1].x - 2000, pts_met1[1].y - 2000)]  
        
    if cur_direction == 1:
      pts_met2.append(pya.Point(pts_met2[cur_point - 1].x + (self.Ln + self.W / 2) * 1000, pts_met2[cur_point - 1].y))
      pts_met1.append(pya.Point(pts_met2[cur_point].x - (self.W + 1) * 1000, pts_met2[cur_point].y - (kW2 * self.W + kS2 * self.S + self.W / 2 + self.Lbx + self.S + (self.W - 7) * 0.5) * 1000 - 21500))
      pts_met1.append(pya.Point(pts_met2[cur_point].x + (self.W / 2 + 1000), pts_met2[cur_point].y + (self.W / 2 + 1) * 1000))
      pts_via2.append(pya.Point(pts_met1[3].x - 2000, pts_met1[3].y - 2000))
      pts_via2.append(pya.Point(pts_met1[3].x - self.W * 1000, pts_met1[3].y - self.W * 1000))
      pts_via2.append(pya.Point(pts_met1[2].x + 2000, pts_met1[2].y + 2000))
      pts_via2.append(pya.Point(pts_met1[2].x + self.W * 1000, pts_met1[2].y + self.W * 1000))
      pts_met2_2 = [pya.Point(pts_met1[2].x + 1000, pts_met1[2].y + 1000), pya.Point(pts_met1[2].x + (self.W + 1) * 1000, pts_met1[2].y + (self.W + 1) * 1000)]
      pts_via3 = [pya.Point(pts_met2[4].x - (self.W / 2 + 1.5) * 1000, pts_met2[4].y + (self.W / 2 + 1.5) * 1000), pya.Point(pts_met2[3].x + (self.W / 2 + 1.5) * 1000, pts_met2[3].y + (self.W / 2 + 1.5) * 1000),
                 pya.Point(pts_met2[3].x + (self.W / 2 + 1.5) * 1000, pts_met2[2].y - (self.W / 2 + 1.5) * 1000), pya.Point(pts_met1[3].x + 4000, pts_met2[2].y - (self.W / 2 + 1.5) * 1000),
                 pya.Point(pts_met1[3].x + 4000, pts_met2[-1].y - (self.W / 2 - (self.W - 7) * 0.5 + (self.S - 7) * 1) * 1000 - 3000), pya.Point(pts_met1[2].x - 4000, pts_met2[-1].y - (self.W / 2 - (self.W - 7) * 0.5 + (self.S - 7) * 1) * 1000 - 3000),
                 pya.Point(pts_met1[2].x - 4000, pts_met2[2].y - (self.W / 2 + 1.5) * 1000), pya.Point(pts_met2[1].x - (self.W / 2 + 1.5) * 1000, pts_met2[2].y - (self.W / 2 + 1.5) * 1000),
                 pya.Point(pts_met2[1].x - (self.W / 2 + 1.5) * 1000, pts_met2[0].y + 1500), pya.Point(pts_met2[4].x - (self.W / 2 + 1.5) * 1000, pts_met2[0].y + 1500)]
      pts_via3_2 = [pya.Point(pts_met1[2].x - 500, pts_met1[2].y - 500), pya.Point(pts_met1[2].x + (self.W + 2.5) * 1000, pts_met1[2].y + (self.W + 2.5) * 1000)]
      

    elif cur_direction == 2:
      pts_met2.append(pya.Point(pts_met2[cur_point - 1].x, pts_met2[cur_point - 1].y + (self.Ln + self.W / 2) * 1000))
      pts_met1.append(pya.Point(pts_met2[cur_point].x - (self.W / 2 + 1) * 1000, pts_met2[cur_point].y - (self.W + 1) * 1000))
      pts_met1.append(pya.Point(pts_met2[cur_point].x + (kW2 * self.W + kS2 * self.S + self.W / 2 + self.Lbx + (self.W - 7) * 0.5) * 1000 + 21500, pts_met2[cur_point].y + 1000))
      pts_via2.append(pya.Point(pts_met1[2].x + 2000, pts_met1[2].y + 2000))
      pts_via2.append(pya.Point(pts_met1[2].x + self.W * 1000, pts_met1[2].y + self.W * 1000))
      pts_via2.append(pya.Point(pts_met1[3].x - 2000, pts_met1[3].y - 2000))
      pts_via2.append(pya.Point(pts_met1[3].x - self.W * 1000, pts_met1[3].y - self.W * 1000))
      pts_met2_2 = [pya.Point(pts_met1[3].x - 1000, pts_met1[3].y - 1000), pya.Point(pts_met1[3].x - (self.W + 1) * 1000, pts_met1[3].y - (self.W + 1) * 1000)]
      pts_via3 = [pya.Point(pts_met2[4].x - (self.W / 2 + 1.5) * 1000, pts_met2[4].y + (self.W / 2 + 1.5) * 1000), pya.Point(pts_met2[3].x + (self.W / 2 + 1.5) * 1000, pts_met2[3].y + (self.W / 2 + 1.5) * 1000),
                  pya.Point(pts_met2[3].x + (self.W / 2 + 1.5) * 1000, pts_met1[3].y + 4000), pya.Point(pts_met2[-1].x + (self.W / 2 - (self.W - 7) * 0.5 + (self.S - 7) * 1) * 1000 + 3000, pts_met1[3].y + 4000),
                  pya.Point(pts_met2[-1].x + (self.W / 2 - (self.W - 7) * 0.5 + (self.S - 7) * 1) * 1000 + 3000, pts_met1[2].y - 4000), pya.Point(pts_met2[3].x + (self.W / 2 + 1.5) * 1000, pts_met1[2].y - 4000),
                  pya.Point(pts_met2[3].x + (self.W / 2 + 1.5) * 1000, pts_met2[2].y - (self.W / 2 + 1.5) * 1000), pya.Point(pts_met2[1].x - (self.W / 2 + 1.5) * 1000, pts_met2[2].y - (self.W / 2 + 1.5) * 1000),
                  pya.Point(pts_met2[1].x - (self.W / 2 + 1.5) * 1000, pts_met2[0].y + 1500), pya.Point(pts_met2[4].x - (self.W / 2 + 1.5) * 1000, pts_met2[0].y + 1500)]
      pts_via3_2 = [pya.Point(pts_met1[3].x + 500, pts_met1[3].y + 500), pya.Point(pts_met1[3].x - (self.W + 2.5) * 1000, pts_met1[3].y - (self.W + 2.5) * 1000)]

    elif cur_direction == 3:
      pts_met2.append(pya.Point(pts_met2[cur_point - 1].x - (self.Ln + self.W / 2) * 1000, pts_met2[cur_point - 1].y))
      pts_met1.append(pya.Point(pts_met2[cur_point].x - 1000, pts_met2[cur_point].y - (self.W / 2 + 1) * 1000))
      pts_met1.append(pya.Point(pts_met2[cur_point].x + (self.W + 1) * 1000, pts_met2[cur_point].y + (kW2 * self.W + kS2 * self.S + self.W / 2 + self.Lbx + (self.W - 7) * 0.5) * 1000 + 21500))
      pts_via2.append(pya.Point(pts_met1[2].x + 2000, pts_met1[2].y + 2000))
      pts_via2.append(pya.Point(pts_met1[2].x + self.W * 1000, pts_met1[2].y + self.W * 1000))
      pts_via2.append(pya.Point(pts_met1[3].x - 2000, pts_met1[3].y - 2000))
      pts_via2.append(pya.Point(pts_met1[3].x - self.W * 1000, pts_met1[3].y - self.W * 1000))
      pts_met2_2 = [pya.Point(pts_met1[3].x - 1000, pts_met1[3].y - 1000), pya.Point(pts_met1[3].x - (self.W + 1) * 1000, pts_met1[3].y - (self.W + 1) * 1000)]
      pts_via3 = [pya.Point(pts_met2[4].x - (self.W / 2 + 1.5) * 1000, pts_met2[4].y + (self.W / 2 + 1.5) * 1000), pya.Point(pts_met1[2].x - 4000, pts_met2[4].y + (self.W / 2 + 1.5) * 1000),
                 pya.Point(pts_met1[2].x - 4000, pts_met2[-1].y + (self.W / 2 - (self.W - 7) * 0.5 + (self.S - 7) * 1) * 1000 + 3000), pya.Point(pts_met1[3].x + 4000, pts_met2[-1].y + (self.W / 2 - (self.W - 7) * 0.5 + (self.S - 7) * 1) * 1000 + 3000),
                 pya.Point(pts_met1[3].x + 4000, pts_met2[4].y + (self.W / 2 + 1.5) * 1000), pya.Point(pts_met2[3].x + (self.W / 2 + 1.5) * 1000, pts_met2[3].y + (self.W / 2 + 1.5) * 1000),
                 pya.Point(pts_met2[3].x + (self.W / 2 + 1.5) * 1000, pts_met2[2].y - (self.W / 2 + 1.5) * 1000), pya.Point(pts_met2[1].x - (self.W / 2 + 1.5) * 1000, pts_met2[2].y - (self.W / 2 + 1.5) * 1000),
                 pya.Point(pts_met2[1].x - (self.W / 2 + 1.5) * 1000, pts_met2[0].y + 1500), pya.Point(pts_met2[4].x - (self.W / 2 + 1.5) * 1000, pts_met2[0].y + 1500)]
      pts_via3_2 = [pya.Point(pts_met1[3].x + 500, pts_met1[3].y + 500), pya.Point(pts_met1[3].x - (self.W + 2.5) * 1000, pts_met1[3].y - (self.W + 2.5) * 1000)]

    elif cur_direction == 4:
      pts_met2.append(pya.Point(pts_met2[cur_point - 1].x, pts_met2[cur_point - 1].y - (self.Ln + self.W / 2) * 1000))
      
      if pts_met2[-1].y - pts_met1[1].y - 1000 <= 25000:
        kW2 += 1
        kS2 += 1
      
      pts_met1.append(pya.Point(pts_met2[cur_point].x - ((kW2 - 1) * self.W + kS2 * self.S + self.W / 2 + self.Lbx + (self.W - 7) * 0.5) * 1000 - 21500, pts_met2[cur_point].y - 1000))
      pts_met1.append(pya.Point(pts_met2[cur_point].x + (self.W / 2 + 1) * 1000, pts_met2[cur_point].y + (self.W + 1) * 1000))
      pts_via2.append(pya.Point(pts_met1[3].x - 2000, pts_met1[3].y - 2000))
      pts_via2.append(pya.Point(pts_met1[3].x - self.W * 1000, pts_met1[3].y - self.W * 1000))
      pts_via2.append(pya.Point(pts_met1[2].x + 2000, pts_met1[2].y + 2000))
      pts_via2.append(pya.Point(pts_met1[2].x + self.W * 1000, pts_met1[2].y + self.W * 1000))
      pts_met2_2 = [pya.Point(pts_met1[2].x + 1000, pts_met1[2].y + 1000), pya.Point(pts_met1[2].x + (self.W + 1) * 1000, pts_met1[2].y + (self.W + 1) * 1000)]
      pts_via3 = [pya.Point(pts_met2[4].x - (self.W / 2 + 1.5) * 1000, pts_met2[4].y + (self.W / 2 + 1.5) * 1000), pya.Point(pts_met2[3].x + (self.W / 2 + 1.5) * 1000, pts_met2[3].y + (self.W / 2 + 1.5) * 1000),
                 pya.Point(pts_met2[3].x + (self.W / 2 + 1.5) * 1000, pts_met2[2].y - (self.W / 2 + 1.5) * 1000), pya.Point(pts_met2[1].x - (self.W / 2 + 1.5) * 1000, pts_met2[2].y - (self.W / 2 + 1.5) * 1000),
                 pya.Point(pts_met2[1].x - (self.W / 2 + 1.5) * 1000, pts_met2[0].y + 1500), pya.Point(pts_met2[4].x - (self.W / 2 + 1.5) * 1000, pts_met2[0].y + 1500),
                 pya.Point(pts_met2[4].x - (self.W / 2 + 1.5) * 1000, pts_met1[2].y - 4000), pya.Point(pts_met2[-1].x - (self.W / 2 - (self.W - 7) * 0.5 + (self.S - 7) * 1) * 1000 - 3000, pts_met1[2].y - 4000),
                 pya.Point(pts_met2[-1].x - (self.W / 2 - (self.W - 7) * 0.5 + (self.S - 7) * 1) * 1000 - 3000, pts_met1[3].y + 4000), pya.Point(pts_met2[4].x - (self.W / 2 + 1.5) * 1000, pts_met1[3].y + 4000)]
      pts_via3_2 = [pya.Point(pts_met1[2].x - 500, pts_met1[2].y - 500), pya.Point(pts_met1[2].x + (self.W + 2.5) * 1000, pts_met1[2].y + (self.W + 2.5) * 1000)]
    
    self.insertBoxes(pts_via2, self.via2_layer)
    self.insertBoxes(pts_met1, self.met1_layer)
    self.insertBoxes(pts_met2_2, self.met2_layer)
    self.insertBoxes(pts_via3_2, self.via3_layer)
    self.cell.shapes(self.met2_layer).insert(pya.Path(pts_met2, self.W * 1000)) 
    self.cell.shapes(self.via3_layer).insert(pya.Polygon(pts_via3))