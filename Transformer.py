import numpy as np
import pandas as pd


class Transformer:
    def __init__(self, name:str, bus1_name:str, bus2_name:str, r:float, x:float):
        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name
        self.r = r
        self.x = x

        self.Yseries = 1/(complex(self.r, self.x))


    def calc_yprim(self):

        ys = self.Yseries

        buses = [self.bus1_name, self.bus2_name]


        return pd.DataFrame([[ys, -ys], [-ys, ys]], index=buses, columns=buses)




if __name__ == "__main__":
    #test
    t1 = Transformer("T1", "bus_1", "bus_2", 0.01, 0.10)



    print(t1.name, t1.bus1_name, t1.bus2_name, t1.r, t1.x)

    print(t1.calc_yprim())