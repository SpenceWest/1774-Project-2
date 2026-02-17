class Load:
    def __init__(self, name: str, bus1_name: str, mw: float, mvar: float):
        self.name = name
        self.bus1_name = bus1_name
        self.mw = mw
        self.mvar = mvar

if __name__ == "__main__":
    # Test case based on the PDF example
    load1 = Load("Load-1", "Bus-2", 50.0, 30.0)
    
    print(load1.name, load1.bus1_name, load1.mw, load1.mvar)
