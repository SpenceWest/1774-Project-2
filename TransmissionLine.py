import numpy as np
import pandas as pd
import numpy as np

class TransmissionLine:
    def __init__(self, name:str, bus1_name:str, bus2_name:str, r:float, x:float, g:float, b:float):
        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name
        self.r = r
        self.x = x
        self.g = g
        self.b = b

        # Milestone 3: Compute and store series admittance Yseries = 1 / (r + jx)
        #              Compute and store shunt admittance Yshunt
        self.Yseries = 1 / (complex(self.r, self.x))
        self.Yshunt = complex(self.g, self.b)

    def calc_yprim(self):

        # Define the 2x2 matrix for a two-terminal series element and shunt capacitive elements
        # Matrix format: [[Yseries + Yshunt/2, -Yseries], [-Yseries, Yseries + Yshunt/2]]
        y_matrix = np.array([
            [self.Yseries + self.Yshunt/2, -self.Yseries],
            [-self.Yseries, self.Yseries + self.Yshunt/2]
        ])

        # Association with bus names as row/column labels
        bus_labels = [self.bus1_name, self.bus2_name]
        df_yprim = pd.DataFrame(y_matrix, index=bus_labels, columns=bus_labels)

        return df_yprim




if __name__ == "__main__":
    #test
    line1 = TransmissionLine("Line 1", "bus_1", "bus_2", 2, 0.25, 0.0, 0.04)



    print(line1.name, line1.bus1_name, line1.bus2_name, line1.r, line1.x, line1.g, line1.b)

    print(line1.calc_yprim())





