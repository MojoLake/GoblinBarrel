import ifcopenshell

file_path = "./data/Ifc2x3_Duplex_Architecture.ifc"



def main():

    demo_file = ifcopenshell.open(file_path)
    walls = demo_file.by_type("IfcWallStandardCase")
    print("numer of walls foumd:", len(walls))



if __name__ == "__main__":
    main()
