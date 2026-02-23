import numpy as np
import pandas as pd

class TransmissionLine:
    def __init__(self, name:str, bus1_name:str, bus2_name:str, r:float, x:float, g:float, b:float):
        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name
        self.r = r
        self.x = x
        self.g = g
        self.b = b

        self.Yseries = 1 / (complex(self.r, self.x))
        self.Yshunt = complex(self.g, self.b)

    def calc_yprim(self):
        ys = self.Yseries
        ysh = self.Yshunt



        buses = [self.bus1_name, self.bus2_name]


        return pd.DataFrame([[ys + ysh/2, -ys], [-ys, ys + ysh/2]], index=buses, columns=buses)




if __name__ == "__main__":
    #test
    line1 = TransmissionLine("Line 1", "bus_1", "bus_2", 0.02, 0.25, 0.0, 0.04)



    print(line1.name, line1.bus1_name, line1.bus2_name, line1.r, line1.x, line1.g, line1.b)

    print(line1.calc_yprim())





