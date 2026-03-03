import pandas as pd


class Transformer:
    def __init__(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float):
        self.name: str = name
        self.bus1_name: str = bus1_name
        self.bus2_name: str = bus2_name
        self.r: float = r
        self.x: float = x
        
        # Milestone 3: Compute and store series admittance Yseries = 1 / (r + jx)
        # Note: r and x are per-unit values entered directly [cite: 13, 14, 16]
        self.Yseries: complex = 1 / complex(self.r, self.x)

    def calc_yprim(self) -> pd.DataFrame:
        """
        Implementation of Milestone 3: Compute the 2x2 primitive admittance matrix. [cite: 17]
        Returns a labeled pandas.DataFrame for clarity. 
        """
        # Define the 2x2 matrix for a two-terminal series element [cite: 53]
        # Matrix format: [[Yseries, -Yseries], [-Yseries, Yseries]]
        y_matrix = np.array([
            [self.Yseries, -self.Yseries],
            [-self.Yseries, self.Yseries]
        ])

        # Association with bus names as row/column labels 
        bus_labels = [self.bus1_name, self.bus2_name]
        df_yprim = pd.DataFrame(y_matrix, index=bus_labels, columns=bus_labels)
        
        return df_yprim

if __name__ == "__main__":
    # Internal validation test according to Milestone 3 requirements [cite: 31-38]
    print("--- Transformer Class Validation ---")
    t1 = Transformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)
    
    # Verify series admittance [cite: 36]
    print(f"Series Admittance (Yseries): {t1.Yseries}")
    
    # Verify the primitive admittance matrix [cite: 38, 48]
    print("\nPrimitive Admittance Matrix (Yprim):")
    print(t1.calc_yprim())
